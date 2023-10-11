#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
from io import IOBase
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import PYTHON_TYPE_MAPPING, SchemaType, merge_schemas
from source_s3.v4.config import S3FileBasedStreamConfig


class UnstructuredParser(FileTypeParser):

    MAX_SIZE_PER_CHUNK = 4_000_000

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
            markdown = self.read_file(fp, logger)
            if not markdown:
                return []
            chunks = [markdown[i : i + self.MAX_SIZE_PER_CHUNK] for i in range(0, len(markdown), self.MAX_SIZE_PER_CHUNK)]
            yield from [
                {
                    "content": chunk,
                    "chunk_number": i,
                    "no_of_chunks": len(chunks),
                    "id": f"{file.uri}_{i}",
                }
                for i, chunk in enumerate(chunks)
            ]

    def read_file(self, file: IOBase, logger: logging.Logger) -> Optional[str]:
        from unstructured.file_utils.filetype import FileType, detect_filetype
        from unstructured.partition.auto import partition
        from unstructured.partition.md import optional_decode

        # set name to none, otherwise unstructured will try to get the modified date from the local file system
        file_name = file.name
        file.name = None
        filetype = detect_filetype(
            file=file,
            file_filename=file_name,
        )
        if filetype == FileType.MD:
            return optional_decode(file.read())
        if not filetype in [FileType.PDF, FileType.DOCX]:
            logger.warn(f"Skipping {file_name}, unsupported file type {str(filetype)}")
            return None
        elements = partition(file=file, metadata_filename=file_name)
        return self._render_markdown(elements)

    def _render_markdown(self, elements: List[Any]) -> str:
        return "\n\n".join([self._convert_to_markdown(el) for el in elements])

    def _convert_to_markdown(self, el: Any) -> str:
        from unstructured.documents.elements import Formula, ListItem, Title

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
