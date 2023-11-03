#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import datetime
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from unittest.mock import Mock, call

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Level,
    Status,
    StreamDescriptor,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from pytest import fixture

logger = logging.getLogger("airbyte")


class MockSource(AbstractSource):
    def __init__(
        self,
        check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None,
        streams: List[Stream] = None,
        per_stream: bool = True,
        message_repository: MessageRepository = None,
        exception_on_missing_stream: bool = True,
    ):
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
        return self._streams

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


def test_successful_check():
    """Tests that if a source returns TRUE for the connection check the appropriate connectionStatus success message is returned"""
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert expected == MockSource(check_lambda=lambda: (True, None)).check(logger, {})


def test_failed_check():
    """Tests that if a source returns FALSE for the connection check the appropriate connectionStatus failure message is returned"""
    expected = AirbyteConnectionStatus(status=Status.FAILED, message="'womp womp'")
    assert expected == MockSource(check_lambda=lambda: (False, "womp womp")).check(logger, {})


def test_raising_check(mocker):
    """Tests that if a source raises an unexpected exception the appropriate connectionStatus failure message is returned."""
    check_lambda = mocker.Mock(side_effect=BaseException("this should fail"))
    with pytest.raises(BaseException):
        MockSource(check_lambda=check_lambda).check(logger, {})


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


def test_discover(mocker):
    """Tests that the appropriate AirbyteCatalog is returned from the discover method"""
    airbyte_stream1 = AirbyteStream(
        name="1",
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        default_cursor_field=["cursor"],
        source_defined_cursor=True,
        source_defined_primary_key=[["pk"]],
    )
    airbyte_stream2 = AirbyteStream(name="2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    stream1 = MockStream()
    stream2 = MockStream()
    mocker.patch.object(stream1, "as_airbyte_stream", return_value=airbyte_stream1)
    mocker.patch.object(stream2, "as_airbyte_stream", return_value=airbyte_stream2)

    expected = AirbyteCatalog(streams=[airbyte_stream1, airbyte_stream2])
    src = MockSource(check_lambda=lambda: (True, None), streams=[stream1, stream2])

    assert expected == src.discover(logger, {})


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


def test_read_stream_emits_repository_message_before_record(mocker, message_repository):
    stream = MockStream(name="my_stream")
    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "read_records", side_effect=[[{"a record": "a value"}, {"another record": "another value"}]])
    message_repository.consume_queue.side_effect = [[message for message in [MESSAGE_FROM_REPOSITORY]], []]

    source = MockSource(streams=[stream], message_repository=message_repository)

    messages = list(source.read(logger, {}, ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])))

    assert messages.count(MESSAGE_FROM_REPOSITORY) == 1
    record_messages = (message for message in messages if message.type == Type.RECORD)
    assert all(messages.index(MESSAGE_FROM_REPOSITORY) < messages.index(record) for record in record_messages)


def test_read_stream_emits_repository_message_on_error(mocker, message_repository):
    stream = MockStream(name="my_stream")
    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "read_records", side_effect=RuntimeError("error"))
    message_repository.consume_queue.return_value = [message for message in [MESSAGE_FROM_REPOSITORY]]

    source = MockSource(streams=[stream], message_repository=message_repository)

    with pytest.raises(RuntimeError):
        messages = list(source.read(logger, {}, ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])))
        assert MESSAGE_FROM_REPOSITORY in messages


def test_read_stream_with_error_gets_display_message(mocker):
    stream = MockStream(name="my_stream")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "read_records", side_effect=RuntimeError("oh no!"))

    source = MockSource(streams=[stream])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])

    # without get_error_display_message
    with pytest.raises(RuntimeError, match="oh no!"):
        list(source.read(logger, {}, catalog))

    mocker.patch.object(MockStream, "get_error_display_message", return_value="my message")

    with pytest.raises(AirbyteTracedException, match="oh no!") as exc:
        list(source.read(logger, {}, catalog))
    assert exc.value.message == "my message"


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


def test_valid_full_refresh_read_no_slices(mocker):
    """Tests that running a full refresh sync on streams which don't specify slices produces the expected AirbyteMessages"""
    stream_output = [{"k1": "v1"}, {"k2": "v2"}]
    s1 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s1")
    s2 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s2")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(s1, SyncMode.full_refresh),
            _configured_stream(s2, SyncMode.full_refresh),
        ]
    )

    expected = _fix_emitted_at(
        [
            _as_stream_status("s1", AirbyteStreamStatus.STARTED),
            _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
            *_as_records("s1", stream_output),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("s2", AirbyteStreamStatus.STARTED),
            _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
            *_as_records("s2", stream_output),
            _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
        ]
    )
    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert expected == messages


def test_valid_full_refresh_read_with_slices(mocker):
    """Tests that running a full refresh sync on streams which use slices produces the expected AirbyteMessages"""
    slices = [{"1": "1"}, {"2": "2"}]
    # When attempting to sync a slice, just output that slice as a record
    s1 = MockStream(
        [({"sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
        name="s1",
    )
    s2 = MockStream(
        [({"sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
        name="s2",
    )

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "stream_slices", return_value=slices)

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(s1, SyncMode.full_refresh),
            _configured_stream(s2, SyncMode.full_refresh),
        ]
    )

    expected = _fix_emitted_at(
        [
            _as_stream_status("s1", AirbyteStreamStatus.STARTED),
            _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
            *_as_records("s1", slices),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("s2", AirbyteStreamStatus.STARTED),
            _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
            *_as_records("s2", slices),
            _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
        ]
    )

    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert expected == messages


@pytest.mark.parametrize(
    "slices",
    [[{"1": "1"}, {"2": "2"}], [{"date": datetime.date(year=2023, month=1, day=1)}, {"date": datetime.date(year=2023, month=1, day=1)}]],
)
def test_read_full_refresh_with_slices_sends_slice_messages(mocker, slices):
    """Given the logger is debug and a full refresh, AirbyteMessages are sent for slices"""
    debug_logger = logging.getLogger("airbyte.debug")
    debug_logger.setLevel(logging.DEBUG)
    stream = MockStream(
        [({"sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
        name="s1",
    )

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "stream_slices", return_value=slices)

    src = MockSource(streams=[stream])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(stream, SyncMode.full_refresh),
        ]
    )

    messages = src.read(debug_logger, {}, catalog)

    assert 2 == len(list(filter(lambda message: message.log and message.log.message.startswith("slice:"), messages)))


def test_read_incremental_with_slices_sends_slice_messages(mocker):
    """Given the logger is debug and a incremental, AirbyteMessages are sent for slices"""
    debug_logger = logging.getLogger("airbyte.debug")
    debug_logger.setLevel(logging.DEBUG)
    slices = [{"1": "1"}, {"2": "2"}]
    stream = MockStream(
        [({"sync_mode": SyncMode.incremental, "stream_slice": s, "stream_state": {}}, [s]) for s in slices],
        name="s1",
    )

    MockStream.supports_incremental = mocker.PropertyMock(return_value=True)
    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "stream_slices", return_value=slices)

    src = MockSource(streams=[stream])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(stream, SyncMode.incremental),
        ]
    )

    messages = src.read(debug_logger, {}, catalog)

    assert 2 == len(list(filter(lambda message: message.log and message.log.message.startswith("slice:"), messages)))


class TestIncrementalRead:
    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(True, id="test_source_emits_state_as_per_stream_format"),
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    def test_with_state_attribute(self, mocker, use_legacy, per_stream_enabled):
        """Test correct state passing for the streams that have a state attribute"""
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]
        old_state = {"cursor": "old_value"}
        if use_legacy:
            input_state = {"s1": old_state}
        else:
            input_state = [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="s1"), stream_state=AirbyteStateBlob.parse_obj(old_state)
                    ),
                ),
            ]
        new_state_from_connector = {"cursor": "new_value"}

        stream_1 = MockStreamWithState(
            [
                (
                    {"sync_mode": SyncMode.incremental, "stream_state": old_state},
                    stream_output,
                )
            ],
            name="s1",
        )
        stream_2 = MockStreamWithState(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s2",
        )
        mocker.patch.object(MockStreamWithState, "get_updated_state", return_value={})
        state_property = mocker.patch.object(
            MockStreamWithState,
            "state",
            new_callable=mocker.PropertyMock,
            return_value=new_state_from_connector,
        )
        mocker.patch.object(MockStreamWithState, "get_json_schema", return_value={})
        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                _as_record("s1", stream_output[0]),
                _as_record("s1", stream_output[1]),
                _as_state({"s1": new_state_from_connector}, "s1", new_state_from_connector)
                if per_stream_enabled
                else _as_state({"s1": new_state_from_connector}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                _as_record("s2", stream_output[0]),
                _as_record("s2", stream_output[1]),
                _as_state({"s1": new_state_from_connector, "s2": new_state_from_connector}, "s2", new_state_from_connector)
                if per_stream_enabled
                else _as_state({"s1": new_state_from_connector, "s2": new_state_from_connector}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )
        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected
        assert state_property.mock_calls == [
            call(old_state),  # set state for s1
            call(),  # get state in the end of slice for s1
            call(),  # get state in the end of slice for s2
        ]

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(True, id="test_source_emits_state_as_per_stream_format"),
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    def test_with_checkpoint_interval(self, mocker, use_legacy, per_stream_enabled):
        """Tests that an incremental read which doesn't specify a checkpoint interval outputs a STATE message
        after reading N records within a stream.
        """
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]

        stream_1 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s1",
        )
        stream_2 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s2",
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})
        # Tell the source to output one state message per record
        mocker.patch.object(
            MockStream,
            "state_checkpoint_interval",
            new_callable=mocker.PropertyMock,
            return_value=1,
        )

        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                _as_record("s1", stream_output[0]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_record("s1", stream_output[1]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                _as_record("s2", stream_output[0]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_record("s2", stream_output[1]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )
        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert expected == messages

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(True, id="test_source_emits_state_as_per_stream_format"),
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    def test_with_no_interval(self, mocker, use_legacy, per_stream_enabled):
        """Tests that an incremental read which doesn't specify a checkpoint interval outputs
        a STATE message only after fully reading the stream and does not output any STATE messages during syncing the stream.
        """
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]

        stream_1 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s1",
        )
        stream_2 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s2",
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})

        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                *_as_records("s1", stream_output),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                *_as_records("s2", stream_output),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert expected == messages

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(True, id="test_source_emits_state_as_per_stream_format"),
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    def test_with_slices(self, mocker, use_legacy, per_stream_enabled):
        """Tests that an incremental read which uses slices outputs each record in the slice followed by a STATE message, for each slice"""
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []
        slices = [{"1": "1"}, {"2": "2"}]
        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]

        stream_1 = MockStream(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s1",
        )
        stream_2 = MockStream(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s2",
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})
        mocker.patch.object(MockStream, "stream_slices", return_value=slices)

        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                # stream 1 slice 1
                *_as_records("s1", stream_output),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                # stream 1 slice 2
                *_as_records("s1", stream_output),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                # stream 2 slice 1
                *_as_records("s2", stream_output),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                # stream 2 slice 2
                *_as_records("s2", stream_output),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert expected == messages

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(True, id="test_source_emits_state_as_per_stream_format"),
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize("slices", [pytest.param([], id="test_slices_as_list"), pytest.param(iter([]), id="test_slices_as_iterator")])
    def test_no_slices(self, mocker, use_legacy, per_stream_enabled, slices):
        """
        Tests that an incremental read returns at least one state messages even if no records were read:
            1. outputs a state message after reading the entire stream
        """
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []

        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]
        state = {"cursor": "value"}
        stream_1 = MockStreamWithState(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s1",
            state=state,
        )
        stream_2 = MockStreamWithState(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s2",
            state=state,
        )

        mocker.patch.object(MockStreamWithState, "supports_incremental", return_value=True)
        mocker.patch.object(MockStreamWithState, "get_json_schema", return_value={})
        mocker.patch.object(MockStreamWithState, "stream_slices", return_value=slices)
        mocker.patch.object(
            MockStreamWithState,
            "state_checkpoint_interval",
            new_callable=mocker.PropertyMock,
            return_value=2,
        )

        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert expected == messages

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(True, id="test_source_emits_state_as_per_stream_format"),
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    def test_with_slices_and_interval(self, mocker, use_legacy, per_stream_enabled):
        """
        Tests that an incremental read which uses slices and a checkpoint interval:
            1. outputs all records
            2. outputs a state message every N records (N=checkpoint_interval)
            3. outputs a state message after reading the entire slice
        """
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []
        slices = [{"1": "1"}, {"2": "2"}]
        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]
        stream_1 = MockStream(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s1",
        )
        stream_2 = MockStream(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s2",
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})
        mocker.patch.object(MockStream, "stream_slices", return_value=slices)
        mocker.patch.object(
            MockStream,
            "state_checkpoint_interval",
            new_callable=mocker.PropertyMock,
            return_value=2,
        )

        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                # stream 1 slice 1
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                _as_record("s1", stream_output[0]),
                _as_record("s1", stream_output[1]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_record("s1", stream_output[2]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                # stream 1 slice 2
                _as_record("s1", stream_output[0]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_record("s1", stream_output[1]),
                _as_record("s1", stream_output[2]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                # stream 2 slice 1
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                _as_record("s2", stream_output[0]),
                _as_record("s2", stream_output[1]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_record("s2", stream_output[2]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                # stream 2 slice 2
                _as_record("s2", stream_output[0]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_record("s2", stream_output[1]),
                _as_record("s2", stream_output[2]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

    @pytest.mark.parametrize(
        "per_stream_enabled",
        [
            pytest.param(False, id="test_source_emits_state_as_per_stream_format"),
        ],
    )
    def test_emit_non_records(self, mocker, per_stream_enabled):
        """
        Tests that an incremental read which uses slices and a checkpoint interval:
            1. outputs all records
            2. outputs a state message every N records (N=checkpoint_interval)
            3. outputs a state message after reading the entire slice
        """

        input_state = []
        slices = [{"1": "1"}, {"2": "2"}]
        stream_output = [
            {"k1": "v1"},
            AirbyteLogMessage(level=Level.INFO, message="HELLO"),
            {"k2": "v2"},
            {"k3": "v3"},
        ]
        stream_1 = MockStreamEmittingAirbyteMessages(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s1",
            state=copy.deepcopy(input_state),
        )
        stream_2 = MockStreamEmittingAirbyteMessages(
            [
                (
                    {
                        "sync_mode": SyncMode.incremental,
                        "stream_slice": s,
                        "stream_state": mocker.ANY,
                    },
                    stream_output,
                )
                for s in slices
            ],
            name="s2",
            state=copy.deepcopy(input_state),
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})
        mocker.patch.object(MockStream, "stream_slices", return_value=slices)
        mocker.patch.object(
            MockStream,
            "state_checkpoint_interval",
            new_callable=mocker.PropertyMock,
            return_value=2,
        )

        src = MockSource(streams=[stream_1, stream_2], per_stream=per_stream_enabled)
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                # stream 1 slice 1
                stream_data_to_airbyte_message("s1", stream_output[0]),
                stream_data_to_airbyte_message("s1", stream_output[1]),
                stream_data_to_airbyte_message("s1", stream_output[2]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                stream_data_to_airbyte_message("s1", stream_output[3]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                # stream 1 slice 2
                stream_data_to_airbyte_message("s1", stream_output[0]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                stream_data_to_airbyte_message("s1", stream_output[1]),
                stream_data_to_airbyte_message("s1", stream_output[2]),
                stream_data_to_airbyte_message("s1", stream_output[3]),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_state({"s1": state}, "s1", state) if per_stream_enabled else _as_state({"s1": state}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                # stream 2 slice 1
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                stream_data_to_airbyte_message("s2", stream_output[0]),
                stream_data_to_airbyte_message("s2", stream_output[1]),
                stream_data_to_airbyte_message("s2", stream_output[2]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                stream_data_to_airbyte_message("s2", stream_output[3]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                # stream 2 slice 2
                stream_data_to_airbyte_message("s2", stream_output[0]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                stream_data_to_airbyte_message("s2", stream_output[1]),
                stream_data_to_airbyte_message("s2", stream_output[2]),
                stream_data_to_airbyte_message("s2", stream_output[3]),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_state({"s1": state, "s2": state}, "s2", state) if per_stream_enabled else _as_state({"s1": state, "s2": state}),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected


def test_checkpoint_state_from_stream_instance():
    teams_stream = MockStreamOverridesStateMethod()
    managers_stream = StreamNoStateMethod()
    state_manager = ConnectorStateManager({"teams": teams_stream, "managers": managers_stream}, [])

    # The stream_state passed to checkpoint_state() should be ignored since stream implements state function
    teams_stream.state = {"updated_at": "2022-09-11"}
    actual_message = teams_stream._checkpoint_state({"ignored": "state"}, state_manager, True)
    assert actual_message == _as_state({"teams": {"updated_at": "2022-09-11"}}, "teams", {"updated_at": "2022-09-11"})

    # The stream_state passed to checkpoint_state() should be used since the stream does not implement state function
    actual_message = managers_stream._checkpoint_state({"updated": "expected_here"}, state_manager, True)
    assert actual_message == _as_state(
        {"teams": {"updated_at": "2022-09-11"}, "managers": {"updated": "expected_here"}}, "managers", {"updated": "expected_here"}
    )
