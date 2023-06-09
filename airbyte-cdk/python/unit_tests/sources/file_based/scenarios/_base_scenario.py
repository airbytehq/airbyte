#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping

from airbyte_cdk.sources.file_based.remote_file import FileType
from unit_tests.sources.file_based.in_memory_files_source import InMemoryFilesSource


class TestScenario:
    def __init__(
        self,
        name: str,
        config: Mapping[str, Any],
        files: Dict[str, Any],
        file_type: FileType,
        expected_catalog: Dict[str, Any],
        expected_records: Dict[str, Any],
        **kwargs,
    ):
        self.name = name
        self.config = config
        self.files = files
        self.file_type = file_type
        self.expected_catalog = expected_catalog
        self.expected_records = expected_records
        self.source = InMemoryFilesSource(self.files, self.file_type)
        self.kwargs = kwargs
        self.validate()

    def validate(self):
        streams = {s["name"] for s in self.config["streams"]}
        expected_streams = {s["name"] for s in self.expected_catalog["streams"]}
        assert expected_streams <= streams

    def configured_catalog(self) -> Dict[str, Any]:
        catalog = {"streams": []}
        for stream in self.expected_catalog["streams"]:
            catalog["streams"].append(
                {
                    "stream": stream,
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            )

        return catalog


class TestScenarioBuilder:
    def __init__(self, **kwargs):
        self._name = ""
        self._config = {}
        self._files = {}
        self._file_type = None
        self._expected_catalog = {}
        self._expected_records = {}
        self.kwargs = kwargs

    def set_name(self, name: str):
        self.name = name
        return self

    def set_config(self, config: Mapping[str, Any]):
        self._config = config
        return self

    def set_files(self, files: Dict[str, Any]):
        self._files = files
        return self

    def set_file_type(self, file_type: FileType):
        self._file_type = file_type
        return self

    def set_expected_catalog(self, expected_catalog: Dict[str, Any]):
        self._expected_catalog = expected_catalog
        return self

    def set_expected_records(self, expected_records: Dict[str, Any]):
        self._expected_records = expected_records
        return self

    def build(self):
        return TestScenario(
            self._name,
            self._config,
            self._files,
            self._file_type,
            self._expected_catalog,
            self._expected_records,
            **self.kwargs,
        )
