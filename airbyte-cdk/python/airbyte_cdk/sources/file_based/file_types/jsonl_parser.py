#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Iterable, List

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class JsonlParser(FileTypeParser):

    MAX_BYTES_PER_FILE_FOR_SCHEMA_INFERENCE = 1_000_000

    async def infer_schema(self, files: List[RemoteFile], stream_reader: AbstractFileBasedStreamReader) -> Dict[str, Any]:
        ...

    def parse_records(self, file: RemoteFile, stream_reader: AbstractFileBasedStreamReader) -> Iterable[Dict[str, Any]]:
        ...
