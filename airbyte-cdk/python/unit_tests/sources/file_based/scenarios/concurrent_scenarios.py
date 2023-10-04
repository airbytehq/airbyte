#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability, StreamAvailable
from airbyte_cdk.sources.streams.concurrent.legacy import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_protocol.models import AirbyteStream, ConfiguredAirbyteStream
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder


class MockStream(AbstractStream):
    def __init__(self, records, name, cursor_field):
        self._records = records
        self._name = name
        self._cursor_field = cursor_field

    def read(self) -> Iterable[Record]:
        yield from self._records

    @property
    def name(self) -> str:
        return self._name

    @property
    def cursor_field(self) -> Optional[str]:
        return self._cursor_field

    def check_availability(self) -> StreamAvailability:
        return StreamAvailable()

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        pass

    def as_airbyte_stream(self) -> AirbyteStream:
        return AirbyteStream(name=self._name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    def log_stream_sync_configuration(self) -> None:
        pass


class ConcurrentCdkSource(AbstractSource):
    def __init__(self, streams: List[AbstractStream]):
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


class ConcurrentSourceBuilder:
    def __init__(self):
        pass

    def build(self, configured_catalog) -> AbstractSource:
        return ConcurrentCdkSource(self._streams)

    def set_streams(self, streams: List[AbstractStream]) -> "ConcurrentSourceBuilder":
        self._streams = streams
        return self


test_concurrent_cdk = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder().set_streams(
            [
                MockStream([Record({"id": "1"}), Record({"id": "2"})], "stream1", None),
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
