#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from io import IOBase
from typing import Any, Dict, List, Mapping

from airbyte_cdk.sources.file_based.file_based_source import AbstractFileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class InMemoryFilesSource(AbstractFileBasedSource):
    def __init__(self, files):
        super().__init__()
        self.files = files

    def stream_reader(self, config: Mapping[str, Any]):
        return InMemoryFilesStreamReader(config, self.files)


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    def __init__(self, _: Mapping[str, Any], files: Dict[str, dict]):
        super().__init__()
        self.files = files

    def list_matching_files(
        self,
        globs: List[str],
    ) -> List[RemoteFile]:
        return [RemoteFile(f, data["last_modified"]) for f, data in self.files.items()]

    def open_file(self, file: RemoteFile) -> IOBase:
        return io.StringIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str):
        if file_name.endswith(".csv"):
            return self._make_csv_file_contents(file_name)
        else:
            raise NotImplementedError(f"No implementation for filename: {file_name}")

    def _make_csv_file_contents(self, file_name: str) -> str:
        fh = io.StringIO()
        writer = csv.writer(fh)
        writer.writerows(self.files[file_name]["contents"])
        return fh.getvalue()
