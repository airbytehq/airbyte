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
from unstructured.documents.elements import Formula, ListItem, Title
from unstructured.file_utils.filetype import FileType, detect_filetype

unstructured_partition = None
unstructured_optional_decode = None


def _import_unstructured() -> None:
    """Dynamically imported as needed, due to slow import speed."""
    global unstructured_partition
    global unstructured_optional_decode
    from unstructured.partition.auto import partition
    from unstructured.partition.md import optional_decode

    unstructured_partition = partition
    unstructured_optional_decode = optional_decode


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
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        with stream_reader.open_file(file, self.file_read_mode, None, logger) as file_handle:
            filetype = self._get_filetype(file_handle, file.uri)

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
            markdown = self._read_file(file_handle, file.uri)
            yield {
                "content": markdown,
                "document_key": file.uri,
            }

    def _read_file(self, file_handle: IOBase, file_name: str) -> str:
        _import_unstructured()
        if (not unstructured_partition) or (not unstructured_optional_decode):
            # check whether unstructured library is actually available for better error message and to ensure proper typing (can't be None after this point)
            raise Exception("unstructured library is not available")

        filetype = self._get_filetype(file_handle, file_name)

        if filetype == FileType.MD:
            file_content: bytes = file_handle.read()
            decoded_content: str = unstructured_optional_decode(file_content)
            return decoded_content
        if filetype not in self._supported_file_types():
            raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD, filename=file_name)

        file: Any = file_handle
        if filetype == FileType.PDF:
            # for PDF, read the file into a BytesIO object because some code paths in pdf parsing are doing an instance check on the file object and don't work with file-like objects
            file_handle.seek(0)
            file = BytesIO(file_handle.read())
            file_handle.seek(0)

        elements = unstructured_partition(file=file, metadata_filename=file_name)
        return self._render_markdown(elements)

    def _get_filetype(self, file: IOBase, file_name: str) -> Any:

        # set name to none, otherwise unstructured will try to get the modified date from the local file system
        if hasattr(file, "name"):
            file.name = None

        return detect_filetype(
            file=file,
            file_filename=file_name,
        )

    def _supported_file_types(self) -> List[Any]:
        return [FileType.MD, FileType.PDF, FileType.DOCX]

    def _render_markdown(self, elements: List[Any]) -> str:
        return "\n\n".join((self._convert_to_markdown(el) for el in elements))

    def _convert_to_markdown(self, el: Any) -> str:
        if isinstance(el, Title):
            heading_str = "#" * (el.metadata.category_depth or 1)
            return f"{heading_str} {el.text}"
        elif isinstance(el, ListItem):
            return f"- {el.text}"
        elif isinstance(el, Formula):
            return f"```\n{el.text}\n```"
        else:
            return str(el.text) if hasattr(el, "text") else ""

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ_BINARY
