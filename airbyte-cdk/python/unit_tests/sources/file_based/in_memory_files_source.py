#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from typing import Dict, List, Optional, Type

from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import FileType, RemoteFile
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream


class InMemoryFilesSource(FileBasedSource):
    def __init__(
            self,
            files,
            file_type,
            availability_strategy: AbstractFileBasedAvailabilityStrategy,
            discovery_policy: AbstractDiscoveryPolicy,
            parsers: Dict[FileType, FileTypeParser],
            stream_cls: Type[AbstractFileBasedStream],
    ):
        super().__init__(
            InMemoryFilesStreamReader(files=files, file_type=file_type),
            availability_strategy=availability_strategy,
            discovery_policy=discovery_policy,
            parsers=parsers,
            stream_cls=stream_cls,
        )
        self.files = files
        self.file_type = file_type
        self.discovery_policy = discovery_policy


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
