#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Optional, Tuple
from unittest.mock import Mock

import freezegun
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import FinalStateCursor


class _MockSource(ConcurrentSourceAdapter):
    def __init__(self, concurrent_source, _streams_to_is_concurrent, logger):
        super().__init__(concurrent_source)
        self._streams_to_is_concurrent = _streams_to_is_concurrent
        self._logger = logger

    message_repository = InMemoryMessageRepository()

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        raise NotImplementedError

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            StreamFacade.create_from_stream(s, self, self._logger, None, FinalStateCursor(stream_name=s.name, stream_namespace=s.namespace, message_repository=InMemoryMessageRepository())) if is_concurrent else s
            for s, is_concurrent in self._streams_to_is_concurrent.items()
        ]


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_adapter():
    concurrent_source = Mock()
    message_from_concurrent_stream = AirbyteMessage(
        type=MessageType.RECORD,
        record=AirbyteRecordMessage(
            stream="s2",
            data={"data": 2},
            emitted_at=1577836800000,
        ),
    )
    concurrent_source.read.return_value = iter([message_from_concurrent_stream])
    regular_stream = _mock_stream("s1", [{"data": 1}])
    concurrent_stream = _mock_stream("s2", [])
    unavailable_stream = _mock_stream("s3", [{"data": 3}], False)
    concurrent_stream.name = "s2"
    logger = Mock()
    adapter = _MockSource(concurrent_source, {regular_stream: False, concurrent_stream: True, unavailable_stream: False}, logger)

    messages = list(adapter.read(logger, {}, _configured_catalog([regular_stream, concurrent_stream, unavailable_stream])))
    records = [m for m in messages if m.type == MessageType.RECORD]

    expected_records = [
        message_from_concurrent_stream,
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream="s1",
                data={"data": 1},
                emitted_at=1577836800000,
            ),
        ),
    ]

    assert records == expected_records


def _mock_stream(name: str, data=[], available: bool = True):
    s = Mock()
    s.name = name
    s.namespace = None
    s.as_airbyte_stream.return_value = AirbyteStream(
        name=name,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    s.check_availability.return_value = (True, None) if available else (False, "not available")
    s.read.return_value = iter(data)
    s.primary_key = None
    return s


def _configured_catalog(streams: List[Stream]):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream.as_airbyte_stream(),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
            for stream in streams
        ]
    )
