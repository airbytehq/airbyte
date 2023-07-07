#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, Iterable, Mapping

import pyarrow as pa
import pyarrow.parquet as pq
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from pyarrow import Scalar


class ParquetParser(FileTypeParser):
    async def infer_schema(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Dict[str, Any]:
        # Pyarrow can detect the schema of a parquet file by reading only its metadata.
        # https://github.com/apache/arrow/blob/main/python/pyarrow/_parquet.pyx#L1168-L1243
        parquet_file = pq.ParquetFile(stream_reader.open_file(file))
        parquet_schema = parquet_file.schema_arrow
        schema = {field.name: ParquetParser.parquet_type_to_schema_type(field.type) for field in parquet_schema}
        return schema

    def parse_records(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Iterable[Dict[str, Any]]:
        table = pq.read_table(stream_reader.open_file(file))
        for batch in table.to_batches():
            for i in range(batch.num_rows):
                row_dict = {column: ParquetParser._to_output_value(batch.column(column)[i]) for column in table.column_names}
                yield row_dict

    @staticmethod
    def _to_output_value(parquet_value: Scalar) -> Any:
        """
        Convert a pyarrow scalar to a value that can be output by the source.
        """
        # Convert date and datetime objects to isoformat strings
        if pa.types.is_time(parquet_value.type) or pa.types.is_timestamp(parquet_value.type) or pa.types.is_date(parquet_value.type):
            return parquet_value.as_py().isoformat()

        # Convert month_day_nano_interval to array
        if parquet_value.type == pa.month_day_nano_interval():
            return json.loads(json.dumps(parquet_value.as_py()))

        # Decode binary strings to utf-8
        if ParquetParser._is_binary(parquet_value.type):
            return parquet_value.as_py().decode("utf-8")
        if pa.types.is_decimal(parquet_value.type):
            return str(parquet_value.as_py())

        # Dictionaries are stored as two columns: indices and values
        # The indices column is an array of integers that maps to the values column
        if pa.types.is_dictionary(parquet_value.type):
            return {
                "indices": parquet_value.indices.tolist(),
                "values": parquet_value.dictionary.tolist(),
            }

        # Convert duration to seconds, then convert to the appropriate unit
        if pa.types.is_duration(parquet_value.type):
            duration = parquet_value.as_py()
            duration_seconds = duration.total_seconds()
            if parquet_value.type.unit == "s":
                return duration_seconds
            elif parquet_value.type.unit == "ms":
                return duration_seconds * 1000
            elif parquet_value.type.unit == "us":
                return duration_seconds * 1_000_000
            elif parquet_value.type.unit == "ns":
                return duration_seconds * 1_000_000_000 + duration.nanoseconds
            else:
                raise ValueError(f"Unknown duration unit: {parquet_value.type.unit}")
        else:
            return parquet_value.as_py()

    @staticmethod
    def parquet_type_to_schema_type(parquet_type: pa.DataType) -> Mapping[str, str]:
        """
        Convert a pyarrow data type to an Airbyte schema type.
        Parquet data types are defined at https://arrow.apache.org/docs/python/api/datatypes.html
        """

        if pa.types.is_timestamp(parquet_type):
            return {"type": "string", "format": "date-time"}
        elif pa.types.is_date(parquet_type):
            return {"type": "string", "format": "date"}
        elif ParquetParser._is_string(parquet_type):
            return {"type": "string"}
        elif pa.types.is_boolean(parquet_type):
            return {"type": "boolean"}
        elif ParquetParser._is_integer(parquet_type):
            return {"type": "integer"}
        elif pa.types.is_floating(parquet_type):
            return {"type": "number"}
        elif ParquetParser._is_object(parquet_type):
            return {"type": "object"}
        elif ParquetParser._is_list(parquet_type):
            return {"type": "array"}
        else:
            raise ValueError(f"Unsupported parquet type: {parquet_type}")

    @staticmethod
    def _is_binary(parquet_type: pa.DataType) -> bool:
        return bool(pa.types.is_binary(parquet_type) or pa.types.is_large_binary(parquet_type))

    @staticmethod
    def _is_integer(parquet_type: pa.DataType) -> bool:
        return bool(pa.types.is_integer(parquet_type) or pa.types.is_duration(parquet_type))

    @staticmethod
    def _is_string(parquet_type: pa.DataType) -> bool:
        return bool(
            pa.types.is_time(parquet_type)
            or pa.types.is_string(parquet_type)
            or pa.types.is_large_string(parquet_type)
            or pa.types.is_decimal(parquet_type)  # Return as a string to ensure no precision is lost
            or ParquetParser._is_binary(parquet_type)  # Best we can do is return as a string since we do not support binary
        )

    @staticmethod
    def _is_object(parquet_type: pa.DataType) -> bool:
        return bool(pa.types.is_dictionary(parquet_type) or pa.types.is_struct(parquet_type))

    @staticmethod
    def _is_list(parquet_type: pa.DataType) -> bool:
        return bool(pa.types.is_list(parquet_type) or pa.types.is_large_list(parquet_type) or parquet_type == pa.month_day_nano_interval())
