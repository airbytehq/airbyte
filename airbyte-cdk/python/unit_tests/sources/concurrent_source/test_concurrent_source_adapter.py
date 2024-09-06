#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple
from unittest.mock import Mock

import freezegun
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    FailureType,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import FinalStateCursor
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class _MockSource(ConcurrentSourceAdapter):
    def __init__(self, concurrent_source, _streams_to_is_concurrent, logger, raise_exception_on_missing_stream=True):
        super().__init__(concurrent_source)
        self._streams_to_is_concurrent = _streams_to_is_concurrent
        self._logger = logger
        self._raise_exception_on_missing_stream = raise_exception_on_missing_stream

    message_repository = InMemoryMessageRepository()

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        raise NotImplementedError

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            StreamFacade.create_from_stream(
                s,
                self,
                self._logger,
                None,
                FinalStateCursor(stream_name=s.name, stream_namespace=s.namespace, message_repository=InMemoryMessageRepository()),
            )
            if is_concurrent
            else s
            for s, is_concurrent in self._streams_to_is_concurrent.items()
        ]

    @property
    def raise_exception_on_missing_stream(self):
        """The getter method."""
        return self._raise_exception_on_missing_stream

    @raise_exception_on_missing_stream.setter
    def raise_exception_on_missing_stream(self, value):
        self._raise_exception_on_missing_stream = value


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_concurrent_source_adapter(as_stream_status, remove_stack_trace):
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
    adapter = _MockSource(concurrent_source, {regular_stream: False, concurrent_stream: True}, logger)
    with pytest.raises(AirbyteTracedException):
        messages = []
        for message in adapter.read(logger, {}, _configured_catalog([regular_stream, concurrent_stream, unavailable_stream])):
            messages.append(message)

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

    unavailable_stream_trace_messages = [
        m
        for m in messages
        if m.type == MessageType.TRACE
        and m.trace.type == TraceType.STREAM_STATUS
        and m.trace.stream_status.status == AirbyteStreamStatus.INCOMPLETE
    ]
    expected_status = [as_stream_status("s3", AirbyteStreamStatus.INCOMPLETE)]

    assert len(unavailable_stream_trace_messages) == 1
    assert unavailable_stream_trace_messages[0].trace.stream_status == expected_status[0].trace.stream_status


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
    s.get_json_schema.return_value = {}
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


@pytest.mark.parametrize("raise_exception_on_missing_stream", [True, False])
def test_read_nonexistent_concurrent_stream_emit_incomplete_stream_status(
    mocker, remove_stack_trace, as_stream_status, raise_exception_on_missing_stream
):
    """
    Tests that attempting to sync a stream which the source does not return from the `streams` method emits incomplete stream status.
    """
    logger = Mock()

    s1 = _mock_stream("s1", [])
    s2 = _mock_stream("this_stream_doesnt_exist_in_the_source", [])

    concurrent_source = Mock()
    concurrent_source.read.return_value = []

    adapter = _MockSource(concurrent_source, {s1: True}, logger)
    expected_status = [as_stream_status("this_stream_doesnt_exist_in_the_source", AirbyteStreamStatus.INCOMPLETE)]

    adapter.raise_exception_on_missing_stream = raise_exception_on_missing_stream

    if not raise_exception_on_missing_stream:
        messages = [remove_stack_trace(message) for message in adapter.read(logger, {}, _configured_catalog([s2]))]
        assert messages[0].trace.stream_status == expected_status[0].trace.stream_status
    else:
        with pytest.raises(AirbyteTracedException) as exc_info:
            messages = [remove_stack_trace(message) for message in adapter.read(logger, {}, _configured_catalog([s2]))]
            assert messages == expected_status
        assert exc_info.value.failure_type == FailureType.config_error
        assert "not found in the source" in exc_info.value.message
