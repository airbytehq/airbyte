#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from io import IOBase
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class ParquetParser(FileTypeParser):
    async def infer_schema(self, file_handle: IOBase, stream_reader: AbstractFileBasedStreamReader) -> Dict[str, Any]:
        ...

    def parse_records(self, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader) -> Iterable[Dict[str, Any]]:
        ...
