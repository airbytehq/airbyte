#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
import logging
from typing import Any, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import (
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, FinalStateCursor
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter
from unit_tests.sources.file_based.scenarios.scenario_builder import SourceBuilder
from unit_tests.sources.streams.concurrent.scenarios.thread_based_concurrent_stream_source_builder import NeverLogSliceLogger

_CURSOR_FIELD = "cursor_field"
_NO_STATE = None


class StreamFacadeConcurrentConnectorStateConverter(EpochValueConcurrentStreamStateConverter):
    pass


class StreamFacadeSource(ConcurrentSourceAdapter):
    def __init__(
        self,
        streams: List[Stream],
        threadpool: concurrent.futures.ThreadPoolExecutor,
        cursor_field: Optional[CursorField] = None,
        cursor_boundaries: Optional[Tuple[str, str]] = None,
        input_state: Optional[List[Mapping[str, Any]]] = _NO_STATE,
    ):
        self._message_repository = InMemoryMessageRepository()
        threadpool_manager = ThreadPoolManager(threadpool, streams[0].logger)
        concurrent_source = ConcurrentSource(threadpool_manager, streams[0].logger, NeverLogSliceLogger(), self._message_repository)
        super().__init__(concurrent_source)
        self._streams = streams
        self._threadpool = threadpool_manager
        self._cursor_field = cursor_field
        self._cursor_boundaries = cursor_boundaries
        self._state = [AirbyteStateMessage(s) for s in input_state] if input_state else None

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        state_manager = ConnectorStateManager(
            state=self._state,
        )  # The input values into the AirbyteStream are dummy values; the connector state manager only uses `name` and `namespace`

        state_converter = StreamFacadeConcurrentConnectorStateConverter()
        stream_states = [state_manager.get_stream_state(stream.name, stream.namespace) for stream in self._streams]
        return [
            StreamFacade.create_from_stream(
                stream,
                self,
                stream.logger,
                state,
                ConcurrentCursor(
                    stream.name,
                    stream.namespace,
                    state,
                    self.message_repository,  # type: ignore  # for this source specifically, we always return `InMemoryMessageRepository`
                    state_manager,
                    state_converter,
                    self._cursor_field,
                    self._cursor_boundaries,
                    None,
                    EpochValueConcurrentStreamStateConverter.get_end_provider(),
                )
                if self._cursor_field
                else FinalStateCursor(
                    stream_name=stream.name, stream_namespace=stream.namespace, message_repository=self.message_repository
                ),
            )
            for stream, state in zip(self._streams, stream_states)
        ]

    @property
    def message_repository(self) -> Union[None, MessageRepository]:
        return self._message_repository

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
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


class StreamFacadeSourceBuilder(SourceBuilder[StreamFacadeSource]):
    def __init__(self):
        self._source = None
        self._streams = []
        self._max_workers = 1
        self._cursor_field = None
        self._cursor_boundaries = None
        self._input_state = None
        self._raw_input_state = None

    def set_streams(self, streams: List[Stream]) -> "StreamFacadeSourceBuilder":
        self._streams = streams
        return self

    def set_max_workers(self, max_workers: int) -> "StreamFacadeSourceBuilder":
        self._max_workers = max_workers
        return self

    def set_incremental(self, cursor_field: CursorField, cursor_boundaries: Optional[Tuple[str, str]]) -> "StreamFacadeSourceBuilder":
        self._cursor_field = cursor_field
        self._cursor_boundaries = cursor_boundaries
        return self

    def set_input_state(self, state: List[Mapping[str, Any]]) -> "StreamFacadeSourceBuilder":
        self._input_state = state
        return self

    def build(
        self, configured_catalog: Optional[Mapping[str, Any]], config: Optional[Mapping[str, Any]], state: Optional[TState]
    ) -> StreamFacadeSource:
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        return StreamFacadeSource(self._streams, threadpool, self._cursor_field, self._cursor_boundaries, state)
