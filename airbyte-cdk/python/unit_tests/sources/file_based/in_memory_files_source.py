#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from logging import Logger
from typing import Callable, Dict, List, Optional, Type

from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.cursor.default_file_based_cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.file_based.stream.file_based_stream_config import FileBasedStreamConfig
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
            cursor_factory: Callable[[FileBasedStreamConfig, Logger], DefaultFileBasedCursor]
    ):
        super().__init__(
            InMemoryFilesStreamReader(files=files, file_type=file_type),
            availability_strategy=availability_strategy,
            discovery_policy=discovery_policy,
            parsers=parsers,
            cursor_factory=cursor_factory
        )
        self.files = files
        self.file_type = file_type
        self.discovery_policy = discovery_policy


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    files: Dict[str, dict]
    file_type: str

    def list_matching_files(
        self,
        globs: List[str],
        from_date: Optional[datetime] = None,
    ) -> List[RemoteFile]:
        return [
            RemoteFile(uri=f, last_modified=datetime.strptime(data["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"), file_type=self.file_type)
            for f, data in self.files.items()
        ]

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
