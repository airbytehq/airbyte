#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Dict, Iterable, Mapping

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
import pyarrow as pa
import pyarrow.parquet as pq


class ParquetParser(FileTypeParser):
    async def infer_schema(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Dict[str, Any]:
        table = self._read_file(file, stream_reader)
        schema = {field.name: ParquetParser.parquet_type_to_schema_type(field.type) for field in table.schema}
        return schema

    def parse_records(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Iterable[Dict[str, Any]]:
        table = self._read_file(file, stream_reader)
        for batch in table.to_batches():
            for i in range(batch.num_rows):
                row_dict = {column: batch.column(column)[i].as_py() for column in table.column_names}
                yield row_dict

    @staticmethod
    def _read_file(file: RemoteFile, stream_reader: AbstractFileBasedStreamReader) -> pa.Table:
        return pq.read_table(stream_reader.open_file(file))

    @staticmethod
    def parquet_type_to_schema_type(parquet_type: pa.DataType) -> Mapping[str, str]:
        # Parquet data types are defined at https://arrow.apache.org/docs/python/api/datatypes.html

        # Types we do not support
        # - binary
        # - month_day_nano_interval
        # - duration

        if pa.types.is_timestamp(parquet_type):
            return {"type": "string", "format": "date-time"}
        elif pa.types.is_time(parquet_type):
            return {"type": "string"}
        elif pa.types.is_string(parquet_type) or pa.types.is_large_string(parquet_type):
            return {"type": "string"}
        elif pa.types.is_decimal(parquet_type):
            return {"type": "string"} # Return as a string to ensure no precision is lost
        elif pa.types.is_boolean(parquet_type):
            return {"type": "boolean"}
        elif pa.types.is_integer(parquet_type):
            return {"type": "integer"}
        elif pa.types.is_floating(parquet_type):
            return {"type": "number"}
        elif pa.types.is_date(parquet_type):
            return {"type": "string", "format": "date"}
        elif pa.types.is_dictionary(parquet_type) or pa.types.is_struct(parquet_type):
            return {"type": "object"}
        elif pa.types.is_list(parquet_type) or pa.types.is_large_list(parquet_type):
            return {"type": "array"}
        else:
            raise ValueError(f"Unsupported parquet type: {parquet_type}")

