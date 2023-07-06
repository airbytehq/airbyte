#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
import pyarrow.parquet as pq
import pandas as pd

class ParquetParser(FileTypeParser):
    async def infer_schema(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Dict[str, Any]:
        raise NotImplementedError()

    def parse_records(
        self, config: FileBasedStreamConfig, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader
    ) -> Iterable[Dict[str, Any]]:

        table = pq.read_table(stream_reader.open_file(file))
        # We convert the table to a pandas dataframe iterating over pyarrow chunks is tricky
        df = table.to_pandas()
        for _, row in df.iterrows():
            logging.warning(f"row: {row}")
            row_dict = row.to_dict()
            logging.warning(f"row_dict: {row_dict}")
            yield row_dict
