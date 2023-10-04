#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy, StreamAvailability, StreamAvailable
from airbyte_cdk.sources.streams.concurrent.legacy import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream
from airbyte_cdk.sources.utils.slice_logger import NeverLogSliceLogger
from airbyte_protocol.models import ConfiguredAirbyteStream
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder


class ConcurrentCdkSource(AbstractSource):
    def __init__(self, streams: List[ThreadBasedConcurrentStream]):
        self._streams = streams

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [StreamFacade(s) for s in self._streams]

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(connectionSpecification={})

    def read_catalog(self, catalog_path: str) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=StreamFacade(s).as_airbyte_stream(),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in self._streams
            ]
        )


class InMemoryPartitionGenerator(PartitionGenerator):
    def __init__(self, partitions: List[Partition]):
        self._partitions = partitions

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        yield from self._partitions


class InMemoryPartition(Partition):
    def __init__(self, name, _slice, records):
        self._name = name
        self._slice = _slice
        self._records = records

    def read(self) -> Iterable[Record]:
        yield from self._records

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        if self._slice:
            # Convert the slice to a string so that it can be hashed
            s = json.dumps(self._slice, sort_keys=True)
            return hash((self._name, s))
        else:
            return hash(self._name)


class ConcurrentSourceBuilder:
    def __init__(self):
        pass

    def build(self, configured_catalog) -> AbstractSource:
        return ConcurrentCdkSource(self._streams)

    def set_streams(self, streams: List[AbstractStream]) -> "ConcurrentSourceBuilder":
        self._streams = streams
        return self


class AlwaysAvailableAvailabilityStrategy(AbstractAvailabilityStrategy):
    def check_availability(self, logger: logging.Logger) -> StreamAvailability:
        return StreamAvailable()


test_concurrent_cdk = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder().set_streams(
            [
                ThreadBasedConcurrentStream(
                    partition_generator=InMemoryPartitionGenerator(
                        [InMemoryPartition("partition1", None, [Record({"id": "1"}), Record({"id": "2"})])]
                    ),
                    max_workers=1,
                    name="stream1",
                    json_schema={},
                    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
                    primary_key=[],
                    cursor_field=None,
                    slice_logger=NeverLogSliceLogger(),
                    logger=logging.getLogger("test_logger"),
                    message_repository=InMemoryMessageRepository(),
                    timeout_seconds=300,
                )
            ]
        )
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                }
            ]
        }
    )
    .build()
)
