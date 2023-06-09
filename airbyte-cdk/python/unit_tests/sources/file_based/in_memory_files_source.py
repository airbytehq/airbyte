#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.sources.file_based.file_based_source import AbstractFileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
)
from airbyte_cdk.sources.file_based.remote_file import FileType, RemoteFile


class InMemoryFilesSource(AbstractFileBasedSource):
    def __init__(self, files, file_type):
        super().__init__()
        self.files = files
        self.file_type = file_type

    def stream_reader(self, config: Mapping[str, Any]):
        return InMemoryFilesStreamReader(files=self.files, file_type=self.file_type)


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    files: Dict[str, dict]
    file_type: FileType

    def list_matching_files(
        self,
        globs: List[str],
        from_date: Optional[datetime] = None,
    ) -> List[RemoteFile]:
        return [
            RemoteFile(f, data["last_modified"], self.file_type)
            for f, data in self.files.items()
        ]

    def open_file(self, file: RemoteFile) -> IOBase:
        return io.StringIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str):
        if self.file_type == FileType.Csv:
            return self._make_csv_file_contents(file_name)
        else:
            raise NotImplementedError(f"No implementation for filename: {file_name}")

    def _make_csv_file_contents(self, file_name: str) -> str:
        fh = io.StringIO()
        writer = csv.writer(fh)
        writer.writerows(self.files[file_name]["contents"])
        return fh.getvalue()
