#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from io import IOBase
from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.file_based.discovery_policy import DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from unit_tests.sources.file_based.in_memory_files_source import InMemoryFilesStreamReader


class LowInferenceLimitDiscoveryPolicy(DefaultDiscoveryPolicy):
    @property
    def max_n_files_for_schema_inference(self):
        return 1


class TestErrorListMatchingFilesInMemoryFilesStreamReader(InMemoryFilesStreamReader):
    def get_matching_files(
        self,
        globs: List[str],
        from_date: Optional[datetime] = None,
    ) -> List[RemoteFile]:
        raise Exception("Error listing files")


class TestErrorOpenFileInMemoryFilesStreamReader(InMemoryFilesStreamReader):
    def open_file(self, file: RemoteFile) -> IOBase:
        raise Exception("Error opening file")


class FailingSchemaValidationPolicy(AbstractSchemaValidationPolicy):
    ALWAYS_FAIL = "always_fail"

    def record_passes_validation_policy(self, record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
        return False


def make_remote_files(files: List[str]) -> List[RemoteFile]:
    return [
        RemoteFile(uri=f, last_modified=datetime.strptime("2023-06-05T03:54:07.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))
        for f in files
    ]
