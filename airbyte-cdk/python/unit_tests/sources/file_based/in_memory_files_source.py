#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from typing import Dict, Iterable, List, Optional, Type

from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class InMemoryFilesSource(FileBasedSource):
    def __init__(
            self,
            files,
            file_type,
            availability_strategy: AvailabilityStrategy,
            discovery_policy: AbstractDiscoveryPolicy,
            parsers: Dict[str, FileTypeParser],
            stream_cls: Type[AbstractFileBasedStream],
    ):
        super().__init__(
            InMemoryFilesStreamReader(files=files, file_type=file_type),
            availability_strategy=availability_strategy,
            discovery_policy=discovery_policy,
            parsers=parsers,
        )
        self.files = files
        self.file_type = file_type
        self.discovery_policy = discovery_policy


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    files: Dict[str, dict]
    file_type: str

    def get_matching_files(
        self,
        globs: List[str],
        from_date: Optional[datetime] = None,
    ) -> Iterable[RemoteFile]:
        yield from AbstractFileBasedStreamReader.filter_files_by_globs([
            RemoteFile(f, datetime.strptime(data["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"), self.file_type)
            for f, data in self.files.items()
        ], globs)

    def open_file(self, file: RemoteFile) -> IOBase:
        return io.StringIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str):
        if self.file_type == "csv":
            return self._make_csv_file_contents(file_name)
        else:
            raise NotImplementedError(f"No implementation for filename: {file_name}")

    def _make_csv_file_contents(self, file_name: str) -> str:
        fh = io.StringIO()
        writer = csv.writer(fh)
        writer.writerows(self.files[file_name]["contents"])
        return fh.getvalue()
