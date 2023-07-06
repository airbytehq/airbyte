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

    # Parquet data types are defined at https://arrow.apache.org/docs/python/api/datatypes.html
    _PARQUET_TYPE_TO_SCHEMA_TYPE = {
        #pa.null(): , NOT SUPPORTED
        pa.bool_(): {"type": "boolean"},

        pa.int8(): {"type": "integer"},
        pa.int16(): {"type": "integer"},
        pa.int32(): {"type": "integer"},
        pa.int64(): {"type": "integer"},
        pa.uint8(): {"type": "integer"},
        pa.uint16(): {"type": "integer"},
        pa.uint32(): {"type": "integer"},
        pa.uint64(): {"type": "integer"},
        pa.float16(): {"type": "number"},
        pa.float32(): {"type": "number"},
        pa.float64(): {"type": "number"},

        #pa.binary(): , NOT SUPPORTED
        pa.date32(): {"type": "string", "format": "date"},
        pa.date64(): {"type": "string", "format": "date"},
        pa.string(): {"type": "string"},
        #pa.duration('us'):, NOT SUPPORTED
        # FIXME: what about objects?
        # What about arrays?
        # What about unions?
    }

    @staticmethod
    def parquet_type_to_schema_type(parquet_type: pa.DataType) -> Mapping[str, str]:
        if pa.types.is_timestamp(parquet_type):
            return {"type": "string", "format": "date-time"}
        elif pa.types.is_time(parquet_type):
            return {"type": "string"}
        else:
            schema_type = ParquetParser._PARQUET_TYPE_TO_SCHEMA_TYPE.get(parquet_type)
            if schema_type is None:
                raise ValueError(f"Unsupported parquet type: {parquet_type}")
            else:
                return schema_type

