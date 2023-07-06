#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Dict, Iterable

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
        schema = {field.name: {"type": str(field.type)} for field in table.schema}
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
