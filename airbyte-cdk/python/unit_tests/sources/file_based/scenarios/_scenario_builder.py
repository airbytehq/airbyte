#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping, Optional, Type

from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy, DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import default_parsers
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream, DefaultFileBasedStream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from unit_tests.sources.file_based.helpers import DefaultTestAvailabilityStrategy
from unit_tests.sources.file_based.in_memory_files_source import InMemoryFilesSource


class TestScenario:
    def __init__(
            self,
            name: str,
            config: Mapping[str, Any],
            files: Dict[str, Any],
            file_type: str,
            expected_catalog: Dict[str, Any],
            expected_records: Dict[str, Any],
            availability_strategy: AvailabilityStrategy,
            discovery_policy: AbstractDiscoveryPolicy,
            parsers: Dict[str, FileTypeParser],
            stream_cls: Type[AbstractFileBasedStream],
            expected_discover_error: Optional[Type[Exception]],
            expected_read_error: Optional[Type[Exception]]
    ):
        self.name = name
        self.config = config
        self.expected_catalog = expected_catalog
        self.expected_records = expected_records
        self.expected_discover_error = expected_discover_error
        self.expected_read_error = expected_read_error
        self.source = InMemoryFilesSource(
            files,
            file_type,
            availability_strategy,
            discovery_policy,
            parsers,
            stream_cls
        )
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
    def __init__(self):
        self._name = ""
        self._config = {}
        self._files = {}
        self._file_type = None
        self._expected_catalog = {}
        self._expected_records = {}
        self._availability_strategy = DefaultTestAvailabilityStrategy()
        self._discovery_policy = DefaultDiscoveryPolicy()
        self._parsers = default_parsers
        self._stream_cls = DefaultFileBasedStream
        self._expected_discover_error = None
        self._expected_read_error = None

    def set_name(self, name: str):
        self._name = name
        return self

    def set_config(self, config: Mapping[str, Any]):
        self._config = config
        return self

    def set_files(self, files: Dict[str, Any]):
        self._files = files
        return self

    def set_file_type(self, file_type: str):
        self._file_type = file_type
        return self

    def set_expected_catalog(self, expected_catalog: Dict[str, Any]):
        self._expected_catalog = expected_catalog
        return self

    def set_expected_records(self, expected_records: Dict[str, Any]):
        self._expected_records = expected_records
        return self

    def set_availability_strategy(self, availability_strategy: AvailabilityStrategy):
        self._availability_strategy = availability_strategy
        return self

    def set_parsers(self, parsers: AbstractDiscoveryPolicy):
        self._parsers = parsers
        return self

    def set_discovery_policy(self, discovery_policy: AbstractDiscoveryPolicy):
        self._discovery_policy = discovery_policy
        return self

    def set_expected_discover_error(self, error: Type[Exception]):
        self._expected_discover_error = error
        return self

    def set_expected_read_error(self, error: Type[Exception]):
        self._expected_read_error = error
        return self

    def build(self):
        return TestScenario(
            self._name,
            self._config,
            self._files,
            self._file_type,
            self._expected_catalog,
            self._expected_records,
            self._availability_strategy,
            self._discovery_policy,
            self._parsers,
            self._stream_cls,
            self._expected_discover_error,
            self._expected_read_error,
        )
