#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import PYTHON_TYPE_MAPPING, merge_schemas


class JsonlParser(FileTypeParser):

    MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE = 1_000_000
    ENCODING = "utf8"

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Dict[str, Any]:
        """
        Infers the schema for the file by inferring the schema for each line, and merging
        it with the previously-inferred schema.
        """
        inferred_schema: Dict[str, Any] = {}
        read_bytes = 0

        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
            for line in fp:
                if read_bytes < self.MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE:
                    line_schema = self.infer_schema_for_record(json.loads(line))
                    inferred_schema = merge_schemas(inferred_schema, line_schema)
                    read_bytes += len(line)

        if read_bytes > self.MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE:
            logger.warning(
                f"Exceeded the maximum number of bytes per file for schema inference ({self.MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE}). "
                f"Inferring schema from an incomplete set of records."
            )

        return inferred_schema

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        """
        This code supports parsing json objects over multiple lines even though this does not align with the JSONL format. This is for
        backward compatibility reasons i.e. the previous source-s3 parser did support this. The drawback is:
        * performance as the way we support json over multiple lines is very brute forced
        * given that we don't have `newlines_in_values` config to scope the possible inputs, we might parse the whole file before knowing if
          the input is improperly formatted or if the json is over multiple lines

        The goal is to run the V4 of source-s3 in production, track the warning log emitted when there are multiline json objects and
        deprecate this feature if it's not a valid use case.
        """
        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
            json_parsing_error = False
            has_multiline_json_object = False
            yielded_at_least_once = False

            accumulator = b""
            for line in fp:
                accumulator += line
                try:
                    record = json.loads(accumulator)
                    if not has_multiline_json_object:
                        logger.warning(f"File at {file.uri} is using multiline JSON. Performance could be greatly reduced")
                        has_multiline_json_object = True

                    yield record
                    yielded_at_least_once = True
                    accumulator = b""
                except json.JSONDecodeError:
                    json_parsing_error = True

            if json_parsing_error and not yielded_at_least_once:
                raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD)

    @classmethod
    def infer_schema_for_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        record_schema = {}
        for key, value in record.items():
            if value is None:
                record_schema[key] = {"type": "null"}
            else:
                record_schema[key] = {"type": PYTHON_TYPE_MAPPING[type(value)]}

        return record_schema

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ
