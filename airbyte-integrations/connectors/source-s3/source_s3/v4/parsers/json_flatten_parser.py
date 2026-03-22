import logging
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import orjson

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
    FileReadMode,
)
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType, schemaless_schema


class JsonFlattenParser(FileTypeParser):
    """
    Parser for JSON files containing a single object with a top-level array key.
    Reads the entire file in one shot, parses with a single orjson.loads() call,
    and yields each element of the array individually.

    Designed for CloudTrail logs: {"Records": [{event1}, {event2}, ...]}
    Each event becomes a separate Airbyte record (one Snowflake row).
    """

    ENCODING = "utf8"

    def __init__(self, flatten_key: str):
        self.flatten_key = flatten_key

    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        return True, None

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        """No-op — this parser is used with schemaless streams (raw VARIANT ingestion)."""
        return schemaless_schema

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
            try:
                content = fp.read()
                data = orjson.loads(content)
            except orjson.JSONDecodeError:
                raise RecordParseError(
                    FileBasedSourceError.ERROR_PARSING_RECORD, filename=file.uri
                )

            if self.flatten_key not in data:
                logger.warning(f"Key '{self.flatten_key}' not found in {file.uri}, skipping")
                return

            records = data[self.flatten_key]
            if not records:
                logger.info(f"Empty '{self.flatten_key}' array in {file.uri}")
                return

            for record in records:
                yield {"data": record}
