#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from io import BytesIO, IOBase
from typing import Any, Dict, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType
from source_s3.v4.config import S3FileBasedStreamConfig


class UnstructuredParser(FileTypeParser):
    @property
    def parser_max_n_files_for_schema_inference(self) -> Optional[int]:
        """
        Just check one file as the schema is static
        """
        return 1

    @property
    def parser_max_n_files_for_parsability(self) -> Optional[int]:
        """
        Do not check any files for parsability because it might be an expensive operation and doesn't give much confidence whether the sync will succeed.
        """
        return 0

    async def infer_schema(
        self,
        config: S3FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        with stream_reader.open_file(file, self.file_read_mode, None, logger) as file_handle:
            filetype = self._get_filetype(file_handle)

            if filetype not in self._supported_file_types():
                raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD, filename=file.uri)

            return {
                "content": {"type": "string"},
                "document_key": {"type": "string"},
            }

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
        with stream_reader.open_file(file, self.file_read_mode, None, logger) as file_handle:
            markdown = self.read_file(file_handle, logger)
            yield {
                "content": markdown,
                "document_key": file.uri,
            }

    def read_file(self, file_handle: IOBase, logger: logging.Logger) -> str:
        from unstructured.file_utils.filetype import FileType
        from unstructured.partition.auto import partition
        from unstructured.partition.md import optional_decode

        file_name = file_handle.name
        filetype = self._get_filetype(file_handle)

        if filetype == FileType.MD:
            return optional_decode(file_handle.read())
        if filetype not in self._supported_file_types():
            raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD, filename=file_name)

        if filetype is FileType.PDF:
            # for PDF, read the file into a BytesIO object because some code paths in pdf parsing are doing an instance check on the file object and don't work with file-like objects
            file_handle.seek(0)
            file = BytesIO(file_handle.read())
            file_handle.seek(0)
        else:
            file = file_handle

        elements = partition(file=file, metadata_filename=file_name)
        return self._render_markdown(elements)

    def _get_filetype(self, file: IOBase):
        from unstructured.file_utils.filetype import detect_filetype

        # set name to none, otherwise unstructured will try to get the modified date from the local file system
        file_name = file.name
        file.name = None
        return detect_filetype(
            file=file,
            file_filename=file_name,
        )

    def _supported_file_types(self):
        from unstructured.file_utils.filetype import FileType

        return [FileType.MD, FileType.PDF, FileType.DOCX]

    def _render_markdown(self, elements: List[Any]) -> str:
        return "\n\n".join((self._convert_to_markdown(el) for el in elements))

    def _convert_to_markdown(self, el: Any) -> str:
        from unstructured.documents.elements import Formula, ListItem, Title

        if type(el) == Title:
            heading_str = "#" * (el.metadata.category_depth or 1)
            return f"{heading_str} {el.text}"
        elif type(el) == ListItem:
            return f"- {el.text}"
        elif type(el) == Formula:
            return f"```\n{el.text}\n```"
        else:
            return el.text if hasattr(el, "text") else ""

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ_BINARY
