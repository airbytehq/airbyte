#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class CsvParser(FileTypeParser):
    async def infer_schema(self, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader) -> Dict[str, Any]:
        with stream_reader.open_file(file) as fp:
            reader = csv.DictReader(fp)
            return {field.strip(): {"type": ["null", "string"]} for field in next(reader)}

    def parse_records(self, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader) -> Iterable[Dict[str, Any]]:
        with stream_reader.open_file(file) as fp:
            reader = csv.DictReader(fp)
            yield from reader
