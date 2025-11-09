import logging

from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
    FileReadMode,
)
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import (
    SchemaType,
)


class LinesParser(FileTypeParser):
    """
    File Lines parser that yields each line as a separate record.
    This parser simply reads each line from the file and outputs it as raw text content.
    """
    MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE = 1_000_000
    ENCODING = "utf8"

    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        """
        LinesParser does not require config checks, implicit pydantic validation is enough.
        """
        return True, None

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        """
        Infers the schema for the file - each line is a simple string record.
        """
        # Simple schema for line-based parsing - just content and line number
        return {
            "content": {"type": "string"}
        }

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
        """
        Parse file lines where each line becomes a separate record.
        """
        yield from self._parse_file_lines(file, stream_reader, logger)

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    def _parse_file_lines(
        self,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        """
        Parse file lines where each line becomes a separate record with content and line number.
        """
        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:

            for line in fp:
                
                # Strip newlines but preserve content
                line_content = line.rstrip('\n\r')
                
                # Skip empty lines
                if not line_content.strip():
                    continue

                # Yield each line as a record with line number and content
                yield {
                    "content": line_content
                }