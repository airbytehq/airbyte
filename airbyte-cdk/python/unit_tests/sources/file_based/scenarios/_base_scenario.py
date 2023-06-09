#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping

from airbyte_cdk.sources.file_based.remote_file import FileType
from unit_tests.sources.file_based.in_memory_files_source import InMemoryFilesSource


class BaseTestScenario:
    name: str
    config: Mapping[str, Any]
    files: Dict[str, Any]
    file_type: FileType
    expected_catalog: Dict[str, Any]
    expected_records: Dict[str, Any]

    def __init__(self):
        self.source = InMemoryFilesSource(self.files, self.file_type)
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
