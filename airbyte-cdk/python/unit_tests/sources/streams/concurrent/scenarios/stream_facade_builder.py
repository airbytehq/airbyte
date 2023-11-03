#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, NoopCursor
from airbyte_cdk.sources.streams.concurrent.state_converter import EpochValueConcurrentStreamStateConverter
from airbyte_protocol.models import ConfiguredAirbyteStream
from unit_tests.sources.file_based.scenarios.scenario_builder import SourceBuilder

_NO_STATE = None


class StreamFacadeConcurrentConnectorStateConverter(EpochValueConcurrentStreamStateConverter):
    pass


class StreamFacadeSource(AbstractSource):
    def __init__(
        self,
        streams: List[Stream],
        max_workers: int,
        cursor_field: Optional[CursorField] = None,
        cursor_boundaries: Optional[Tuple[str, str]] = None,
        input_state: Optional[List[Mapping[str, Any]]] = _NO_STATE,
    ):
        self._streams = streams
        self._max_workers = max_workers
        self._message_repository = InMemoryMessageRepository()
        self._cursor_field = cursor_field
        self._cursor_boundaries = cursor_boundaries
        self._state = [AirbyteStateMessage.parse_obj(s) for s in input_state] if input_state else None

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        state_manager = ConnectorStateManager(stream_instance_map={s.name: s for s in self._streams}, state=self._state)
        state_converter = StreamFacadeConcurrentConnectorStateConverter("created")
        return [
            StreamFacade.create_from_stream(
                stream,
                self,
                stream.logger,
                self._max_workers,
                state_converter.get_concurrent_stream_state(state_manager.get_stream_state(stream.name, stream.namespace)),
                ConcurrentCursor(
                    stream.name,
                    stream.namespace,
                    state_converter.get_concurrent_stream_state(state_manager.get_stream_state(stream.name, stream.namespace)),
                    self.message_repository,  # type: ignore  # for this source specifically, we always return `InMemoryMessageRepository`
                    state_manager,
                    state_converter,
                    self._cursor_field,
                    self._cursor_boundaries,
                )
                if self._cursor_field
                else NoopCursor(),
            )
            for stream in self._streams
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

    def build(self, configured_catalog: Optional[Mapping[str, Any]]) -> StreamFacadeSource:
        return StreamFacadeSource(self._streams, self._max_workers, self._cursor_field, self._cursor_boundaries, self._input_state)
