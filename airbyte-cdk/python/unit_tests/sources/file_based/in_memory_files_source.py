#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from typing import Dict, List, Optional

from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import FileType, RemoteFile


class InMemoryFilesSource(FileBasedSource):
    def __init__(self, files, file_type, discovery_policy=None):
        super().__init__(InMemoryFilesStreamReader(files=files, file_type=file_type))
        self.files = files
        self.file_type = file_type
        self._discovery_policy = discovery_policy

    @property
    def discovery_policy(self):
        return self._discovery_policy


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
