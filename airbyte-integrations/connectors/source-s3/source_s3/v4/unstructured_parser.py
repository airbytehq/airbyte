from io import IOBase
from source_s3.v4.config import S3FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
import json
import logging
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import PYTHON_TYPE_MAPPING, SchemaType, merge_schemas
from unstructured.partition.auto import partition
from unstructured.documents.elements import Element, Title, ListItem, Formula

class UnstructuredParser(FileTypeParser):

    MAX_SIZE_PER_CHUNK = 500

    async def infer_schema(
        self,
        config: S3FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        return {
            "content": {"type": "string"},
            "chunk_number": {"type": "integer"},
            "no_of_chunks": {"type": "integer"},
            "id": {"type": "string"},
            # todo add meta data
        }

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
        with stream_reader.open_file(file, self.file_read_mode, None, logger) as fp:
            markdown = self.read_file(fp)
            chunks = [markdown[i:i+self.MAX_SIZE_PER_CHUNK] for i in range(0, len(markdown), self.MAX_SIZE_PER_CHUNK)]
            yield from [{
                "content": chunk,
                "chunk_number": i,
                "no_of_chunks": len(chunks),
                "id": f"{file.uri}_{i}",
            } for i, chunk in enumerate(chunks)]
    
    def read_file(self, file: IOBase) -> str:
        # set name to none, otherwise unstructured will try to get the modified date from the local file system
        file_name = file.name
        file.name = None
        ## TODO - do not partition markdown but pass through as-is
        elements = partition(file=file, metadata_filename=file_name)
        return self.render_markdown(elements)

    def render_markdown(self, elements: List[Element]) -> str:
        return "\n\n".join([self.convert_to_markdown(el) for el in elements])
    
    def convert_to_markdown(self, el: Element) -> str:
        if type(el) == Title:
            return f"# {el.text}"
        elif type(el) == ListItem:
            return f"- {el.text}"
        elif type(el) == Formula:
            return f"```\n{el.text}\n```"
        else:
            return el.text

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ_BINARY
