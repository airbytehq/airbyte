#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from datetime import timedelta
from typing import Any, Callable, Iterator, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.abstract_stream_facade import AbstractStreamFacade
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, Cursor, CursorField, CursorValueType, FinalStateCursor, GapType
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import AbstractStreamStateConverter

DEFAULT_LOOKBACK_SECONDS = 0


class ConcurrentSourceAdapter(AbstractSource, ABC):
    def __init__(self, concurrent_source: ConcurrentSource, **kwargs: Any) -> None:
        """
        ConcurrentSourceAdapter is a Source that wraps a concurrent source and exposes it as a regular source.

        The source's streams are still defined through the streams() method.
        Streams wrapped in a StreamFacade will be processed concurrently.
        Other streams will be processed sequentially as a later step.
        """
        self._concurrent_source = concurrent_source
        super().__init__(**kwargs)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[List[AirbyteStateMessage]] = None,
    ) -> Iterator[AirbyteMessage]:
        abstract_streams = self._select_abstract_streams(config, catalog)
        concurrent_stream_names = {stream.name for stream in abstract_streams}
        configured_catalog_for_regular_streams = ConfiguredAirbyteCatalog(
            streams=[stream for stream in catalog.streams if stream.stream.name not in concurrent_stream_names]
        )
        if abstract_streams:
            yield from self._concurrent_source.read(abstract_streams)
        if configured_catalog_for_regular_streams.streams:
            yield from super().read(logger, config, configured_catalog_for_regular_streams, state)

    def _select_abstract_streams(self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog) -> List[AbstractStream]:
        """
        Selects streams that can be processed concurrently and returns their abstract representations.
        """
        all_streams = self.streams(config)
        stream_name_to_instance: Mapping[str, Stream] = {s.name: s for s in all_streams}
        abstract_streams: List[AbstractStream] = []
        for configured_stream in configured_catalog.streams:
            stream_instance = stream_name_to_instance.get(configured_stream.stream.name)
            if not stream_instance:
                continue

            if isinstance(stream_instance, AbstractStreamFacade):
                abstract_streams.append(stream_instance.get_underlying_stream())
        return abstract_streams

    def convert_to_concurrent_stream(
        self, logger: logging.Logger, stream: Stream, state_manager: ConnectorStateManager, cursor: Optional[Cursor] = None
    ) -> Stream:
        """
        Prepares a stream for concurrent processing by initializing or assigning a cursor,
        managing the stream's state, and returning an updated Stream instance.
        """
        state: MutableMapping[str, Any] = {}

        if cursor:
            state = state_manager.get_stream_state(stream.name, stream.namespace)

            stream.cursor = cursor  # type: ignore[assignment]  # cursor is of type ConcurrentCursor, which inherits from Cursor
            if hasattr(stream, "parent"):
                stream.parent.cursor = cursor
        else:
            cursor = FinalStateCursor(
                stream_name=stream.name,
                stream_namespace=stream.namespace,
                message_repository=self.message_repository,  # type: ignore[arg-type]  # _default_message_repository will be returned in the worst case
            )
        return StreamFacade.create_from_stream(stream, self, logger, state, cursor)

    def initialize_cursor(
        self,
        stream: Stream,
        state_manager: ConnectorStateManager,
        converter: AbstractStreamStateConverter,
        slice_boundary_fields: Optional[Tuple[str, str]],
        start: Optional[CursorValueType],
        end_provider: Callable[[], CursorValueType],
        lookback_window: Optional[GapType] = None,
        slice_range: Optional[GapType] = None,
    ) -> Optional[ConcurrentCursor]:
        lookback_window = lookback_window or timedelta(seconds=DEFAULT_LOOKBACK_SECONDS)

        cursor_field_name = stream.cursor_field

        if cursor_field_name:
            if not isinstance(cursor_field_name, str):
                raise ValueError(f"Cursor field type must be a string, but received {type(cursor_field_name).__name__}.")

            return ConcurrentCursor(
                stream.name,
                stream.namespace,
                state_manager.get_stream_state(stream.name, stream.namespace),
                self.message_repository,  # type: ignore[arg-type]  # _default_message_repository will be returned in the worst case
                state_manager,
                converter,
                CursorField(cursor_field_name),
                slice_boundary_fields,
                start,
                end_provider,
                lookback_window,
                slice_range,
            )

        return None
