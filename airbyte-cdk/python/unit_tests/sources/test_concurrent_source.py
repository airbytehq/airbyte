#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from pytest import fixture

logger = logging.getLogger("airbyte")


class MockSource(ConcurrentSource):
    def __init__(
        self,
        check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None,
        streams: List[Stream] = None,
        per_stream: bool = True,
        message_repository: MessageRepository = InMemoryMessageRepository(),
        exception_on_missing_stream: bool = True,
    ):
        super().__init__(1, 10, message_repository)
        self._streams = streams
        self.check_lambda = check_lambda
        self.per_stream = per_stream
        self.exception_on_missing_stream = exception_on_missing_stream
        self._message_repository = message_repository

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        if self.check_lambda:
            return self.check_lambda()
        return False, "Missing callable."

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not self._streams:
            raise Exception("Stream is not set")
        return [StreamFacade.create_from_stream(stream, self, logger, None, NoopCursor()) for stream in self._streams]

    @property
    def raise_exception_on_missing_stream(self) -> bool:
        return self.exception_on_missing_stream

    @property
    def per_stream_state_enabled(self) -> bool:
        return self.per_stream

    @property
    def message_repository(self):
        return self._message_repository


class StreamNoStateMethod(Stream):
    name = "managers"
    primary_key = None

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        return {}


class MockStreamOverridesStateMethod(Stream, IncrementalMixin):
    name = "teams"
    primary_key = None
    cursor_field = "updated_at"
    _cursor_value = ""
    start_date = "1984-12-12"

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        return {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {self.cursor_field: self._cursor_value} if self._cursor_value else {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, self.start_date)


MESSAGE_FROM_REPOSITORY = Mock()


@fixture
def message_repository():
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = [message for message in [MESSAGE_FROM_REPOSITORY]]
    return message_repository


class MockStream(Stream):
    def __init__(
        self,
        inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Iterable[Mapping[str, Any]]]] = None,
        name: str = None,
    ):
        self._inputs_and_mocked_outputs = inputs_and_mocked_outputs
        self._name = name

    @property
    def name(self):
        return self._name

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:  # type: ignore
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if self._inputs_and_mocked_outputs:
            for _input, output in self._inputs_and_mocked_outputs:
                if kwargs == _input:
                    return output

        raise Exception(f"No mocked output supplied for input: {kwargs}. Mocked inputs/outputs: {self._inputs_and_mocked_outputs}")

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "pk"


class MockStreamWithState(MockStream):
    cursor_field = "cursor"

    def __init__(self, inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Iterable[Mapping[str, Any]]]], name: str, state=None):
        super().__init__(inputs_and_mocked_outputs, name)
        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        pass


class MockStreamEmittingAirbyteMessages(MockStreamWithState):
    def __init__(
        self, inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Iterable[AirbyteMessage]]] = None, name: str = None, state=None
    ):
        super().__init__(inputs_and_mocked_outputs, name, state)
        self._inputs_and_mocked_outputs = inputs_and_mocked_outputs
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "pk"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {self.cursor_field: self._cursor_value} if self._cursor_value else {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, self.start_date)


def test_read_nonexistent_stream_raises_exception(mocker):
    """Tests that attempting to sync a stream which the source does not return from the `streams` method raises an exception"""
    s1 = MockStream(name="s1")
    s2 = MockStream(name="this_stream_doesnt_exist_in_the_source")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})

    src = MockSource(streams=[s1])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s2, SyncMode.full_refresh)])
    with pytest.raises(KeyError):
        list(src.read(logger, {}, catalog))


def test_read_nonexistent_stream_without_raises_exception(mocker):
    """Tests that attempting to sync a stream which the source does not return from the `streams` method raises an exception"""
    s1 = MockStream(name="s1")
    s2 = MockStream(name="this_stream_doesnt_exist_in_the_source")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})

    src = MockSource(streams=[s1], exception_on_missing_stream=False)

    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s2, SyncMode.full_refresh)])
    messages = list(src.read(logger, {}, catalog))

    assert messages == []


def test_read_stream_emits_repository_message_on_error(mocker, message_repository):
    stream = MockStream(name="my_stream")
    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "read_records", side_effect=RuntimeError("error"))

    source = MockSource(streams=[stream], message_repository=message_repository)

    with pytest.raises(RuntimeError):
        messages = list(source.read(logger, {}, ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])))
        assert MESSAGE_FROM_REPOSITORY in messages


GLOBAL_EMITTED_AT = 1


def _as_record(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=GLOBAL_EMITTED_AT),
    )


def _as_records(stream: str, data: List[Dict[str, Any]]) -> List[AirbyteMessage]:
    return [_as_record(stream, datum) for datum in data]


def _as_stream_status(stream: str, status: AirbyteStreamStatus) -> AirbyteMessage:
    trace_message = AirbyteTraceMessage(
        emitted_at=datetime.datetime.now().timestamp() * 1000.0,
        type=TraceType.STREAM_STATUS,
        stream_status=AirbyteStreamStatusTraceMessage(
            stream_descriptor=StreamDescriptor(name=stream),
            status=status,
        ),
    )

    return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)


def _as_state(state_data: Dict[str, Any], stream_name: str = "", per_stream_state: Dict[str, Any] = None):
    if per_stream_state:
        return AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name=stream_name), stream_state=AirbyteStateBlob.parse_obj(per_stream_state)
                ),
                data=state_data,
            ),
        )
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state_data))


def _configured_stream(stream: Stream, sync_mode: SyncMode):
    return ConfiguredAirbyteStream(
        stream=stream.as_airbyte_stream(),
        sync_mode=sync_mode,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )


def _fix_emitted_at(messages: List[AirbyteMessage]) -> List[AirbyteMessage]:
    for msg in messages:
        if msg.type == Type.RECORD and msg.record:
            msg.record.emitted_at = GLOBAL_EMITTED_AT
        if msg.type == Type.TRACE and msg.trace:
            msg.trace.emitted_at = GLOBAL_EMITTED_AT
    return messages
