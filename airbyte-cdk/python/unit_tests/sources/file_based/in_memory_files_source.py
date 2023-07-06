#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from typing import Any, Dict, Iterable, List, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.file_based.default_file_based_availability_strategy import DefaultFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import DEFAULT_SCHEMA_VALIDATION_POLICIES, AbstractSchemaValidationPolicy
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class InMemoryFilesSource(FileBasedSource):
    def __init__(
            self,
            files,
            file_type,
            availability_strategy: AvailabilityStrategy,
            discovery_policy: AbstractDiscoveryPolicy,
            validation_policies: Dict[str, AbstractSchemaValidationPolicy],
            parsers: Dict[str, FileTypeParser],
            stream_reader: AbstractFileBasedStreamReader,
            catalog: Optional[Dict[str, Any]],
            file_write_options: Dict[str, Any],
    ):
        stream_reader = stream_reader or InMemoryFilesStreamReader(files=files, file_type=file_type, file_write_options=file_write_options)
        availability_strategy = availability_strategy or DefaultFileBasedAvailabilityStrategy(stream_reader)
        super().__init__(
            stream_reader,
            catalog=ConfiguredAirbyteCatalog(streams=catalog["streams"]) if catalog else None,
            availability_strategy=availability_strategy,
            discovery_policy=discovery_policy,
            parsers=parsers,
            validation_policies=validation_policies or DEFAULT_SCHEMA_VALIDATION_POLICIES,
        )

        # Attributes required for test purposes
        self.files = files
        self.file_type = file_type


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    files: Dict[str, dict]
    file_type: str
    file_write_options: Optional[Dict[str, Any]]

    def get_matching_files(
        self,
        globs: List[str],
    ) -> Iterable[RemoteFile]:
        yield from AbstractFileBasedStreamReader.filter_files_by_globs([
            RemoteFile(uri=f, last_modified=datetime.strptime(data["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"), file_type=self.file_type)
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
        if self.file_write_options:
            csv.register_dialect("in_memory_dialect", **self.file_write_options)
            writer = csv.writer(fh, dialect="in_memory_dialect")
            writer.writerows(self.files[file_name]["contents"])
            csv.unregister_dialect("in_memory_dialect")
        else:
            writer = csv.writer(fh)
            writer.writerows(self.files[file_name]["contents"])
        return fh.getvalue()
