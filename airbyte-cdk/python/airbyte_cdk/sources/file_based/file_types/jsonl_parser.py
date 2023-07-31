#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import PYTHON_TYPE_MAPPING, merge_schemas


class JsonlParser(FileTypeParser):

    MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE = 1_000_000

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

        with stream_reader.open_file(file) as fp:
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
        with stream_reader.open_file(file) as fp:
            for line in fp:
                yield json.loads(line)

    @classmethod
    def infer_schema_for_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        record_schema = {}
        for key, value in record.items():
            if value is None:
                record_schema[key] = {"type": "null"}
            else:
                record_schema[key] = {"type": PYTHON_TYPE_MAPPING[type(value)]}

        return record_schema
