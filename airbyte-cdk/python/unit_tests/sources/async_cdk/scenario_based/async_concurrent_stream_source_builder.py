#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources.abstract_source_async import AsyncAbstractSource
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.core_async import AsyncStream
from airbyte_cdk.sources.streams.availability_strategy_async import AsyncAvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_protocol.models import ConfiguredAirbyteStream
from unit_tests.sources.scenario_based.scenario_builder import SourceBuilder


class AsyncConcurrentCdkSource(AsyncAbstractSource):
    def __init__(self, streams: List[AsyncStream]):
        self._streams = streams
        super().__init__()

    async def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        # Check is not verified because it is up to the source to implement this method
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[AsyncStream]:
        return self._streams

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(connectionSpecification={})

    def read_catalog(self, catalog_path: str) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=s.as_airbyte_stream(),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in self._streams
            ]
        )


class ConcurrentSourceBuilder(SourceBuilder[AsyncConcurrentCdkSource]):
    def __init__(self):
        self._streams: List[AsyncStream] = []
        self._message_repository = None

    def build(self, configured_catalog: Optional[Mapping[str, Any]]) -> AsyncConcurrentCdkSource:
        return AsyncConcurrentCdkSource(self._streams)

    def set_streams(self, streams: List[AsyncStream]) -> "ConcurrentSourceBuilder":
        self._streams = streams
        return self

    def set_message_repository(self, message_repository: MessageRepository) -> "ConcurrentSourceBuilder":
        self._message_repository = message_repository
        return self


class AlwaysAvailableAvailabilityStrategy(AsyncAvailabilityStrategy):
    async def check_availability(self, stream: AsyncStream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
        return True, None


class LocalAsyncStream(AsyncStream):
    def __init__(
            self,
            name: str,
            json_schema: Mapping[str, Any],
            availability_strategy: Optional[AsyncAvailabilityStrategy],
            primary_key: Any,  # TODO
            cursor_field: Any,  # TODO
            slices: List[List[Mapping[str, Any]]]
    ):
        self._name = name
        self._json_schema = json_schema
        self._availability_strategy = availability_strategy
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._slices = slices

    @property
    def name(self):
        return self._name

    async def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        if stream_slice:
            for record in stream_slice:
                yield record
        else:
            raise NotImplementedError

    async def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in self._slices:
            yield stream_slice

    @property
    def availability_strategy(self) -> Optional[AsyncAvailabilityStrategy]:
        return self._availability_strategy

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema
