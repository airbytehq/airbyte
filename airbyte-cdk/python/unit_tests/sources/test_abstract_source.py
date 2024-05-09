#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import datetime
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteErrorTraceMessage,
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
    FailureType,
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
from airbyte_cdk.sources.streams.checkpoint import IncrementalCheckpointReader
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.utils.airbyte_secrets_utils import update_secrets
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from pytest import fixture

logger = logging.getLogger("airbyte")


class MockSource(AbstractSource):
    def __init__(
        self,
        check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None,
        streams: List[Stream] = None,
        message_repository: MessageRepository = None,
        exception_on_missing_stream: bool = True,
        stop_sync_on_stream_failure: bool = False,
    ):
        self._streams = streams
        self.check_lambda = check_lambda
        self.exception_on_missing_stream = exception_on_missing_stream
        self._message_repository = message_repository
        self._stop_sync_on_stream_failure = stop_sync_on_stream_failure

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


class MockSourceWithStopSyncFalseOverride(MockSource):
    @property
    def stop_sync_on_stream_failure(self) -> bool:
        return False


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


class StreamRaisesException(Stream):
    name = "lamentations"
    primary_key = None

    def __init__(self, exception_to_raise):
        self._exception_to_raise = exception_to_raise

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        raise self._exception_to_raise


MESSAGE_FROM_REPOSITORY = Mock()


@fixture
def message_repository():
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = [message for message in [MESSAGE_FROM_REPOSITORY]]
    return message_repository


def test_successful_check():
    """Tests that if a source returns TRUE for the connection check the appropriate connectionStatus success message is returned"""
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert MockSource(check_lambda=lambda: (True, None)).check(logger, {}) == expected


def test_failed_check():
    """Tests that if a source returns FALSE for the connection check the appropriate connectionStatus failure message is returned"""
    expected = AirbyteConnectionStatus(status=Status.FAILED, message="'womp womp'")
    assert MockSource(check_lambda=lambda: (False, "womp womp")).check(logger, {}) == expected


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

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return ["updated_at"]


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
        self._cursor_value = value.get(self.cursor_field)


class MockResumableFullRefreshStream(Stream):
    def __init__(
        self,
        inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Mapping[str, Any]]] = None,
        name: str = None,
    ):
        self._inputs_and_mocked_outputs = inputs_and_mocked_outputs
        self._name = name
        self._state = {}

    @property
    def name(self):
        return self._name

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:  # type: ignore
        output = None
        next_page_token = {}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if self._inputs_and_mocked_outputs:
            for _input, mocked_output in self._inputs_and_mocked_outputs:
                if kwargs == _input:
                    if "error" in mocked_output:
                        raise AirbyteTracedException(message=mocked_output.get("error"))
                    else:
                        next_page_token = mocked_output.get("next_page")
                        output = mocked_output.get("records")

        if output is None:
            raise Exception(f"No mocked output supplied for input: {kwargs}. Mocked inputs/outputs: {self._inputs_and_mocked_outputs}")

        self.state = next_page_token
        yield from output

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value


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

    assert src.discover(logger, {}) == expected


def test_read_nonexistent_stream_raises_exception(mocker):
    """Tests that attempting to sync a stream which the source does not return from the `streams` method raises an exception"""
    s1 = MockStream(name="s1")
    s2 = MockStream(name="this_stream_doesnt_exist_in_the_source")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})

    src = MockSource(streams=[s1])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s2, SyncMode.full_refresh)])
    with pytest.raises(AirbyteTracedException) as exc_info:
        list(src.read(logger, {}, catalog))

    assert exc_info.value.failure_type == FailureType.config_error
    assert "not found in the source" in exc_info.value.internal_message


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
    message_repository.consume_queue.side_effect = [[message for message in [MESSAGE_FROM_REPOSITORY]], [], []]

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

    with pytest.raises(AirbyteTracedException):
        messages = list(source.read(logger, {}, ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])))
        assert MESSAGE_FROM_REPOSITORY in messages


def test_read_stream_with_error_gets_display_message(mocker):
    stream = MockStream(name="my_stream")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "read_records", side_effect=RuntimeError("oh no!"))

    source = MockSource(streams=[stream])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(stream, SyncMode.full_refresh)])

    # without get_error_display_message
    with pytest.raises(AirbyteTracedException):
        list(source.read(logger, {}, catalog))

    mocker.patch.object(MockStream, "get_error_display_message", return_value="my message")

    with pytest.raises(AirbyteTracedException) as exc:
        list(source.read(logger, {}, catalog))
    assert "oh no!" in exc.value.message


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


def _as_state(stream_name: str = "", per_stream_state: Dict[str, Any] = None):
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name), stream_state=AirbyteStateBlob.parse_obj(per_stream_state)
            ),
        ),
    )


def _as_error_trace(
    stream: str, error_message: str, internal_message: Optional[str], failure_type: Optional[FailureType], stack_trace: Optional[str]
) -> AirbyteMessage:
    trace_message = AirbyteTraceMessage(
        emitted_at=datetime.datetime.now().timestamp() * 1000.0,
        type=TraceType.ERROR,
        error=AirbyteErrorTraceMessage(
            stream_descriptor=StreamDescriptor(name=stream),
            message=error_message,
            internal_message=internal_message,
            failure_type=failure_type,
            stack_trace=stack_trace,
        ),
    )

    return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)


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
    s1 = MockStream([({"stream_slice": {}, "stream_state": {}, "sync_mode": SyncMode.full_refresh}, stream_output)], name="s1")
    s2 = MockStream([({"stream_slice": {}, "stream_state": {}, "sync_mode": SyncMode.full_refresh}, stream_output)], name="s2")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(MockStream, "cursor_field", return_value=[])

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
            _as_state("s1", {"__ab_no_cursor_state_message": True}),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("s2", AirbyteStreamStatus.STARTED),
            _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
            *_as_records("s2", stream_output),
            _as_state("s2", {"__ab_no_cursor_state_message": True}),
            _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
        ]
    )
    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert messages == expected


def test_valid_full_refresh_read_with_slices(mocker):
    """Tests that running a full refresh sync on streams which use slices produces the expected AirbyteMessages"""
    slices = [{"1": "1"}, {"2": "2"}]
    # When attempting to sync a slice, just output that slice as a record
    s1 = MockStream(
        [({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
        name="s1",
    )
    s2 = MockStream(
        [({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
        name="s2",
    )

    mocker.patch.object(MockStream, "cursor_field", return_value=None)
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
            _as_state("s1", {"__ab_no_cursor_state_message": True}),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("s2", AirbyteStreamStatus.STARTED),
            _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
            *_as_records("s2", slices),
            _as_state("s2", {"__ab_no_cursor_state_message": True}),
            _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
        ]
    )

    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert messages == expected


# Delete this test as it's no longer relevant since we honor incoming state
def test_full_refresh_does_not_use_incoming_state(mocker):
    """Tests that running a full refresh sync does not use an incoming state message from the platform"""
    pass
    # We'll actually removed this filtering logic and will rely on the platform to dicate whether to pass state to the connector
    # So in reality we can probably get rid of this test entirely
    # slices = [{"1": "1"}, {"2": "2"}]
    # When attempting to sync a slice, just output that slice as a record

    # s1 = MockStream(
    #     [({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
    #     name="s1",
    # )
    # s2 = MockStream(
    #     [({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
    #     name="s2",
    # )
    #
    # def stream_slices_side_effect(stream_state: Mapping[str, Any], **kwargs) -> List[Mapping[str, Any]]:
    #     if stream_state:
    #         return slices[1:]
    #     else:
    #         return slices
    #
    # mocker.patch.object(MockStream, "get_json_schema", return_value={})
    # mocker.patch.object(MockStream, "stream_slices", side_effect=stream_slices_side_effect)
    #
    # state = [
    #     AirbyteStateMessage(
    #         type=AirbyteStateType.STREAM,
    #         stream=AirbyteStreamState(
    #             stream_descriptor=StreamDescriptor(name="s1"),
    #             stream_state=AirbyteStateBlob.parse_obj({"created_at": "2024-01-31"}),
    #         ),
    #     ),
    #     AirbyteStateMessage(
    #         type=AirbyteStateType.STREAM,
    #         stream=AirbyteStreamState(
    #             stream_descriptor=StreamDescriptor(name="s2"),
    #             stream_state=AirbyteStateBlob.parse_obj({"__ab_no_cursor_state_message": True}),
    #         ),
    #     ),
    # ]
    #
    # src = MockSource(streams=[s1, s2])
    # catalog = ConfiguredAirbyteCatalog(
    #     streams=[
    #         _configured_stream(s1, SyncMode.full_refresh),
    #         _configured_stream(s2, SyncMode.full_refresh),
    #     ]
    # )
    #
    # expected = _fix_emitted_at(
    #     [
    #         _as_stream_status("s1", AirbyteStreamStatus.STARTED),
    #         _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
    #         *_as_records("s1", slices),
    #         _as_state("s1", {"__ab_no_cursor_state_message": True}),
    #         _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
    #         _as_stream_status("s2", AirbyteStreamStatus.STARTED),
    #         _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
    #         *_as_records("s2", slices),
    #         _as_state("s2", {"__ab_no_cursor_state_message": True}),
    #         _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
    #     ]
    # )
    #
    # messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state)))
    #
    # assert messages == expected


@pytest.mark.parametrize(
    "slices",
    [[{"1": "1"}, {"2": "2"}], [{"date": datetime.date(year=2023, month=1, day=1)}, {"date": datetime.date(year=2023, month=1, day=1)}]],
)
def test_read_full_refresh_with_slices_sends_slice_messages(mocker, slices):
    """Given the logger is debug and a full refresh, AirbyteMessages are sent for slices"""
    debug_logger = logging.getLogger("airbyte.debug")
    debug_logger.setLevel(logging.DEBUG)
    stream = MockStream(
        [({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": s}, [s]) for s in slices],
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
    def test_with_state_attribute(self, mocker, use_legacy):
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
                    {"sync_mode": SyncMode.incremental, "stream_slice": {}, "stream_state": old_state},
                    stream_output,
                )
            ],
            name="s1",
        )
        stream_2 = MockStreamWithState(
            [({"sync_mode": SyncMode.incremental, "stream_slice": {}, "stream_state": {}}, stream_output)],
            name="s2",
        )
        mocker.patch.object(MockStreamWithState, "get_updated_state", return_value={})

        # Mock the stream's getter property for each time the stream reads self.state while syncing a stream
        getter_mock = Mock(wraps=MockStreamWithState.state.fget)
        getter_mock.side_effect = [
            old_state,  # stream s1: Setting the checkpoint reader state to self.state if implemented
            old_state,  # stream s1: observe state after first record
            old_state,  # stream s1: observe state after second record
            new_state_from_connector,  # stream s2: observe state after first slice
            {},  # stream s2: Setting the checkpoint reader state to self.state if implemented
            {},  # stream s2: observe state after first record
            {},  # stream s2: observe state after second record
            new_state_from_connector,  # stream s2: observe state after first slice
        ]
        mock_get_property = MockStreamWithState.state.getter(getter_mock)
        state_property = mocker.patch.object(
            MockStreamWithState,
            "state",
            mock_get_property,
        )

        mocker.patch.object(MockStreamWithState, "get_json_schema", return_value={})
        src = MockSource(streams=[stream_1, stream_2])
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
                _as_state("s1", new_state_from_connector),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                _as_record("s2", stream_output[0]),
                _as_record("s2", stream_output[1]),
                _as_state("s2", new_state_from_connector),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )
        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

        # The state getter is called when we call the stream's observe method. We call self.state at the start of each stream (2 times),
        # once for each record (4 times), and at the end of each slice (2 times)
        assert len(state_property.fget.mock_calls) == 8

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    def test_with_checkpoint_interval(self, mocker, use_legacy):
        """Tests that an incremental read which doesn't specify a checkpoint interval outputs a STATE message
        after reading N records within a stream.
        """
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]

        stream_1 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_slice": {}, "stream_state": {}}, stream_output)],
            name="s1",
        )
        stream_2 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_slice": {}, "stream_state": {}}, stream_output)],
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

        src = MockSource(streams=[stream_1, stream_2])
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
                _as_state("s1", state),
                _as_record("s1", stream_output[1]),
                _as_state("s1", state),
                _as_state("s1", state),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                _as_record("s2", stream_output[0]),
                _as_state("s2", state),
                _as_record("s2", stream_output[1]),
                _as_state("s2", state),
                _as_state("s2", state),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )
        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    def test_with_no_interval(self, mocker, use_legacy):
        """Tests that an incremental read which doesn't specify a checkpoint interval outputs
        a STATE message only after fully reading the stream and does not output any STATE messages during syncing the stream.
        """
        if use_legacy:
            input_state = defaultdict(dict)
        else:
            input_state = []
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]

        stream_1 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_slice": {}, "stream_state": {}}, stream_output)],
            name="s1",
        )
        stream_2 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_slice": {}, "stream_state": {}}, stream_output)],
            name="s2",
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})

        src = MockSource(streams=[stream_1, stream_2])
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
                _as_state("s1", state),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                *_as_records("s2", stream_output),
                _as_state("s2", state),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    def test_with_slices(self, mocker, use_legacy):
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

        src = MockSource(streams=[stream_1, stream_2])
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
                _as_state("s1", state),
                # stream 1 slice 2
                *_as_records("s1", stream_output),
                _as_state("s1", state),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                # stream 2 slice 1
                *_as_records("s2", stream_output),
                _as_state("s2", state),
                # stream 2 slice 2
                *_as_records("s2", stream_output),
                _as_state("s2", state),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    @pytest.mark.parametrize("slices", [pytest.param([], id="test_slices_as_list"), pytest.param(iter([]), id="test_slices_as_iterator")])
    def test_no_slices(self, mocker, use_legacy, slices):
        """
        Tests that an incremental read returns at least one state messages even if no records were read:
            1. outputs a state message after reading the entire stream
        """
        state = {"cursor": "value"}
        if use_legacy:
            input_state = {"s1": state, "s2": state}
        else:
            input_state = [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="s1"), stream_state=AirbyteStateBlob.parse_obj(state)
                    ),
                ),
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="s2"), stream_state=AirbyteStateBlob.parse_obj(state)
                    ),
                ),
            ]

        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]
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

        src = MockSource(streams=[stream_1, stream_2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(stream_1, SyncMode.incremental),
                _configured_stream(stream_2, SyncMode.incremental),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_state("s1", state),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_state("s2", state),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

    @pytest.mark.parametrize(
        "use_legacy",
        [
            pytest.param(True, id="test_incoming_stream_state_as_legacy_format"),
            pytest.param(False, id="test_incoming_stream_state_as_per_stream_format"),
        ],
    )
    def test_with_slices_and_interval(self, mocker, use_legacy):
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

        src = MockSource(streams=[stream_1, stream_2])
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
                _as_state("s1", state),
                _as_record("s1", stream_output[2]),
                _as_state("s1", state),
                # stream 1 slice 2
                _as_record("s1", stream_output[0]),
                _as_state("s1", state),
                _as_record("s1", stream_output[1]),
                _as_record("s1", stream_output[2]),
                _as_state("s1", state),
                _as_state("s1", state),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                # stream 2 slice 1
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                _as_record("s2", stream_output[0]),
                _as_record("s2", stream_output[1]),
                _as_state("s2", state),
                _as_record("s2", stream_output[2]),
                _as_state("s2", state),
                # stream 2 slice 2
                _as_record("s2", stream_output[0]),
                _as_state("s2", state),
                _as_record("s2", stream_output[1]),
                _as_record("s2", stream_output[2]),
                _as_state("s2", state),
                _as_state("s2", state),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected

    def test_emit_non_records(self, mocker):
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
        getter_mock = Mock(wraps=MockStreamEmittingAirbyteMessages.state.fget)
        getter_mock.return_value = state
        mock_get_property = MockStreamEmittingAirbyteMessages.state.getter(getter_mock)
        mocker.patch.object(
            MockStreamEmittingAirbyteMessages,
            "state",
            mock_get_property,
        )

        # mocker.patch.object(MockStreamWithState, "get_updated_state", return_value=state)
        mocker.patch.object(MockStreamWithState, "supports_incremental", return_value=True)
        mocker.patch.object(MockStreamWithState, "get_json_schema", return_value={})
        mocker.patch.object(MockStreamWithState, "stream_slices", return_value=slices)
        mocker.patch.object(
            MockStreamWithState,
            "state_checkpoint_interval",
            new_callable=mocker.PropertyMock,
            return_value=2,
        )

        src = MockSource(streams=[stream_1, stream_2])
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
                _as_state("s1", state),
                stream_data_to_airbyte_message("s1", stream_output[3]),
                _as_state("s1", state),
                # stream 1 slice 2
                stream_data_to_airbyte_message("s1", stream_output[0]),
                _as_state("s1", state),
                stream_data_to_airbyte_message("s1", stream_output[1]),
                stream_data_to_airbyte_message("s1", stream_output[2]),
                stream_data_to_airbyte_message("s1", stream_output[3]),
                _as_state("s1", state),
                _as_state("s1", state),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
                # stream 2 slice 1
                _as_stream_status("s2", AirbyteStreamStatus.STARTED),
                _as_stream_status("s2", AirbyteStreamStatus.RUNNING),
                stream_data_to_airbyte_message("s2", stream_output[0]),
                stream_data_to_airbyte_message("s2", stream_output[1]),
                stream_data_to_airbyte_message("s2", stream_output[2]),
                _as_state("s2", state),
                stream_data_to_airbyte_message("s2", stream_output[3]),
                _as_state("s2", state),
                # stream 2 slice 2
                stream_data_to_airbyte_message("s2", stream_output[0]),
                _as_state("s2", state),
                stream_data_to_airbyte_message("s2", stream_output[1]),
                stream_data_to_airbyte_message("s2", stream_output[2]),
                stream_data_to_airbyte_message("s2", stream_output[3]),
                _as_state("s2", state),
                _as_state("s2", state),
                _as_stream_status("s2", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=input_state)))

        assert messages == expected


class TestResumableFullRefreshRead:
    def test_resumable_full_refresh_multiple_pages(self, mocker):
        """Tests that running a resumable full refresh sync from the first attempt with no prior state"""
        responses = [
            {"records": [{"1": "1"}, {"2": "2"}], "next_page": {"page": 1}},
            {"records": [{"3": "3"}, {"4": "4"}], "next_page": {"page": 2}},
            {"records": [{"3": "3"}, {"4": "4"}]},
        ]
        # When attempting to sync a slice, just output that slice as a record

        # We've actually removed this filtering logic and will rely on the platform to dicate whether to pass state to the connector
        # So in reality we can probably get rid of this test entirely
        s1 = MockResumableFullRefreshStream(
            [
                ({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": {}}, responses[0]),
                ({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 1}}, responses[1]),
                ({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 2}}, responses[2]),
            ],
            name="s1",
        )

        mocker.patch.object(MockResumableFullRefreshStream, "get_json_schema", return_value={})

        src = MockSource(streams=[s1])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.full_refresh),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                *_as_records("s1", responses[0]["records"]),
                _as_state("s1", {"page": 1}),
                *_as_records("s1", responses[1]["records"]),
                _as_state("s1", {"page": 2}),
                *_as_records("s1", responses[2]["records"]),
                _as_state("s1", {}),
                _as_state("s1", {}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

        assert messages == expected

    def test_resumable_full_refresh_with_incoming_state(self, mocker):
        """Tests that running a resumable full refresh sync from the second attempt with partial state passed in"""
        responses = [
            {"records": [{"100": "100"}, {"200": "200"}], "next_page": {"page": 11}},
            {"records": [{"300": "300"}, {"400": "400"}], "next_page": {"page": 12}},
            {"records": [{"500": "500"}, {"600": "600"}], "next_page": {"page": 13}},
            {"records": [{"700": "700"}, {"800": "800"}]},
        ]
        # When attempting to sync a slice, just output that slice as a record

        # We've actually removed this filtering logic and will rely on the platform to dicate whether to pass state to the connector
        # So in reality we can probably get rid of this test entirely
        s1 = MockResumableFullRefreshStream(
            [
                ({"stream_state": {"page": 10}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 10}}, responses[0]),
                ({"stream_state": {"page": 10}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 11}}, responses[1]),
                ({"stream_state": {"page": 10}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 12}}, responses[2]),
                ({"stream_state": {"page": 10}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 13}}, responses[3]),
            ],
            name="s1",
        )

        mocker.patch.object(MockResumableFullRefreshStream, "get_json_schema", return_value={})

        state = [
            AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="s1"),
                    stream_state=AirbyteStateBlob.parse_obj({"page": 10}),
                ),
            )
        ]

        src = MockSource(streams=[s1])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.full_refresh),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                *_as_records("s1", responses[0]["records"]),
                _as_state("s1", {"page": 11}),
                *_as_records("s1", responses[1]["records"]),
                _as_state("s1", {"page": 12}),
                *_as_records("s1", responses[2]["records"]),
                _as_state("s1", {"page": 13}),
                *_as_records("s1", responses[3]["records"]),
                _as_state("s1", {}),
                _as_state("s1", {}),
                _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            ]
        )

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state)))

        assert messages == expected

    def test_resumable_full_refresh_partial_failure(self, mocker):
        """Tests that running a resumable full refresh sync from the first attempt that fails before completing successfully"""
        expected_error_message = "I have failed you Anakin."
        responses = [
            {"records": [{"1": "1"}, {"2": "2"}], "next_page": {"page": 1}},
            {"records": [{"3": "3"}, {"4": "4"}], "next_page": {"page": 2}},
            {"error": expected_error_message},
        ]
        # When attempting to sync a slice, just output that slice as a record

        # We've actually removed this filtering logic and will rely on the platform to dicate whether to pass state to the connector
        # So in reality we can probably get rid of this test entirely
        s1 = MockResumableFullRefreshStream(
            [
                ({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": {}}, responses[0]),
                ({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 1}}, responses[1]),
                ({"stream_state": {}, "sync_mode": SyncMode.full_refresh, "stream_slice": {"page": 2}}, responses[2]),
            ],
            name="s1",
        )

        mocker.patch.object(MockResumableFullRefreshStream, "get_json_schema", return_value={})

        src = MockSource(streams=[s1])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.full_refresh),
            ]
        )

        expected = _fix_emitted_at(
            [
                _as_stream_status("s1", AirbyteStreamStatus.STARTED),
                _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
                *_as_records("s1", responses[0]["records"]),
                _as_state("s1", {"page": 1}),
                *_as_records("s1", responses[1]["records"]),
                _as_state("s1", {"page": 2}),
                _as_stream_status("s1", AirbyteStreamStatus.INCOMPLETE),
                _as_error_trace("s1", expected_error_message, None, FailureType.system_error, None),
            ]
        )

        messages = []
        with pytest.raises(AirbyteTracedException) as exc:
            for message in src.read(logger, {}, catalog):
                messages.append(_remove_stack_trace(message))

        assert _fix_emitted_at(messages) == expected
        assert "s1" in exc.value.message
        assert exc.value.failure_type == FailureType.config_error


def test_observe_state_from_stream_instance():
    teams_stream = MockStreamOverridesStateMethod()
    managers_stream = StreamNoStateMethod()
    state_manager = ConnectorStateManager(
        {
            "teams": AirbyteStream(
                name="teams", namespace="", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
            ),
            "managers": AirbyteStream(
                name="managers", namespace="", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
            ),
        },
        [],
    )

    teams_checkpoint_reader = IncrementalCheckpointReader(stream_slices=[], stream_state={})
    managers_checkpoint_reader = IncrementalCheckpointReader(stream_slices=[], stream_state={})

    # The stream_state passed to checkpoint_state() should be ignored since stream implements state function
    teams_stream.state = {"updated_at": "2022-09-11"}
    teams_stream._observe_state(teams_checkpoint_reader, {"ignored": "state"})
    actual_message = teams_stream._checkpoint_state(stream_state=teams_checkpoint_reader.get_checkpoint(), state_manager=state_manager)
    assert actual_message == _as_state("teams", {"updated_at": "2022-09-11"})

    # The stream_state passed to checkpoint_state() should be used since the stream does not implement state function
    managers_stream._observe_state(managers_checkpoint_reader, {"updated": "expected_here"})
    actual_message = managers_stream._checkpoint_state(
        stream_state=managers_checkpoint_reader.get_checkpoint(), state_manager=state_manager
    )
    assert actual_message == _as_state("managers", {"updated": "expected_here"})

    # Stream_state None when passed to checkpoint_state() should be ignored and retain the existing state value
    managers_stream._observe_state(managers_checkpoint_reader)
    actual_message = managers_stream._checkpoint_state(
        stream_state=managers_checkpoint_reader.get_checkpoint(), state_manager=state_manager
    )
    assert actual_message == _as_state("managers", {"updated": "expected_here"})


@pytest.mark.parametrize(
    "exception_to_raise,expected_error_message,expected_internal_message",
    [
        pytest.param(
            AirbyteTracedException(message="I was born only to crash like Icarus"),
            "I was born only to crash like Icarus",
            None,
            id="test_raises_traced_exception",
        ),
        pytest.param(
            Exception("Generic connector error message"),
            "Something went wrong in the connector. See the logs for more details.",
            "Generic connector error message",
            id="test_raises_generic_exception",
        ),
    ],
)
def test_continue_sync_with_failed_streams(mocker, exception_to_raise, expected_error_message, expected_internal_message):
    """
    Tests that running a sync for a connector with multiple streams will continue syncing when one stream fails
    with an error. This source does not override the default behavior defined in the AbstractSource class.
    """
    stream_output = [{"k1": "v1"}, {"k2": "v2"}]
    s1 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s1")
    s2 = StreamRaisesException(exception_to_raise=exception_to_raise)
    s3 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s3")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(StreamRaisesException, "get_json_schema", return_value={})

    src = MockSource(streams=[s1, s2, s3])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(s1, SyncMode.full_refresh),
            _configured_stream(s2, SyncMode.full_refresh),
            _configured_stream(s3, SyncMode.full_refresh),
        ]
    )

    expected = _fix_emitted_at(
        [
            _as_stream_status("s1", AirbyteStreamStatus.STARTED),
            _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
            *_as_records("s1", stream_output),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("lamentations", AirbyteStreamStatus.STARTED),
            _as_stream_status("lamentations", AirbyteStreamStatus.INCOMPLETE),
            _as_error_trace("lamentations", expected_error_message, expected_internal_message, FailureType.system_error, None),
            _as_stream_status("s3", AirbyteStreamStatus.STARTED),
            _as_stream_status("s3", AirbyteStreamStatus.RUNNING),
            *_as_records("s3", stream_output),
            _as_stream_status("s3", AirbyteStreamStatus.COMPLETE),
        ]
    )

    with pytest.raises(AirbyteTracedException) as exc:
        messages = [_remove_stack_trace(message) for message in src.read(logger, {}, catalog)]
        messages = _fix_emitted_at(messages)

        assert messages == expected

    assert "lamentations" in exc.value.message
    assert exc.value.failure_type == FailureType.config_error


def test_continue_sync_source_override_false(mocker):
    """
    Tests that running a sync for a connector explicitly overriding the default AbstractSource.stop_sync_on_stream_failure
    property to be False which will continue syncing stream even if one encountered an exception.
    """
    update_secrets(["API_KEY_VALUE"])

    stream_output = [{"k1": "v1"}, {"k2": "v2"}]
    s1 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s1")
    s2 = StreamRaisesException(exception_to_raise=AirbyteTracedException(message="I was born only to crash like Icarus"))
    s3 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s3")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(StreamRaisesException, "get_json_schema", return_value={})

    src = MockSourceWithStopSyncFalseOverride(streams=[s1, s2, s3])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(s1, SyncMode.full_refresh),
            _configured_stream(s2, SyncMode.full_refresh),
            _configured_stream(s3, SyncMode.full_refresh),
        ]
    )

    expected = _fix_emitted_at(
        [
            _as_stream_status("s1", AirbyteStreamStatus.STARTED),
            _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
            *_as_records("s1", stream_output),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("lamentations", AirbyteStreamStatus.STARTED),
            _as_stream_status("lamentations", AirbyteStreamStatus.INCOMPLETE),
            _as_error_trace("lamentations", "I was born only to crash like Icarus", None, FailureType.system_error, None),
            _as_stream_status("s3", AirbyteStreamStatus.STARTED),
            _as_stream_status("s3", AirbyteStreamStatus.RUNNING),
            *_as_records("s3", stream_output),
            _as_stream_status("s3", AirbyteStreamStatus.COMPLETE),
        ]
    )

    with pytest.raises(AirbyteTracedException) as exc:
        messages = [_remove_stack_trace(message) for message in src.read(logger, {}, catalog)]
        messages = _fix_emitted_at(messages)

        assert messages == expected

    assert "lamentations" in exc.value.message
    assert exc.value.failure_type == FailureType.config_error


def test_sync_error_trace_messages_obfuscate_secrets(mocker):
    """
    Tests that exceptions emitted as trace messages by a source have secrets properly sanitized
    """
    update_secrets(["API_KEY_VALUE"])

    stream_output = [{"k1": "v1"}, {"k2": "v2"}]
    s1 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s1")
    s2 = StreamRaisesException(
        exception_to_raise=AirbyteTracedException(message="My api_key value API_KEY_VALUE flew too close to the sun.")
    )
    s3 = MockStream([({"sync_mode": SyncMode.full_refresh}, stream_output)], name="s3")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(StreamRaisesException, "get_json_schema", return_value={})

    src = MockSource(streams=[s1, s2, s3])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(s1, SyncMode.full_refresh),
            _configured_stream(s2, SyncMode.full_refresh),
            _configured_stream(s3, SyncMode.full_refresh),
        ]
    )

    expected = _fix_emitted_at(
        [
            _as_stream_status("s1", AirbyteStreamStatus.STARTED),
            _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
            *_as_records("s1", stream_output),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("lamentations", AirbyteStreamStatus.STARTED),
            _as_stream_status("lamentations", AirbyteStreamStatus.INCOMPLETE),
            _as_error_trace("lamentations", "My api_key value **** flew too close to the sun.", None, FailureType.system_error, None),
            _as_stream_status("s3", AirbyteStreamStatus.STARTED),
            _as_stream_status("s3", AirbyteStreamStatus.RUNNING),
            *_as_records("s3", stream_output),
            _as_stream_status("s3", AirbyteStreamStatus.COMPLETE),
        ]
    )

    with pytest.raises(AirbyteTracedException) as exc:
        messages = [_remove_stack_trace(message) for message in src.read(logger, {}, catalog)]
        messages = _fix_emitted_at(messages)

        assert messages == expected

    assert "lamentations" in exc.value.message
    assert exc.value.failure_type == FailureType.config_error


def test_continue_sync_with_failed_streams_with_override_false(mocker):
    """
    Tests that running a sync for a connector with multiple streams and stop_sync_on_stream_failure enabled stops
    the sync when one stream fails with an error.
    """
    stream_output = [{"k1": "v1"}, {"k2": "v2"}]
    s1 = MockStream([({"stream_state": {}, "stream_slice": {}, "sync_mode": SyncMode.full_refresh}, stream_output)], name="s1")
    s2 = StreamRaisesException(AirbyteTracedException(message="I was born only to crash like Icarus"))
    s3 = MockStream([({"stream_state": {}, "stream_slice": {}, "sync_mode": SyncMode.full_refresh}, stream_output)], name="s3")

    mocker.patch.object(MockStream, "get_json_schema", return_value={})
    mocker.patch.object(StreamRaisesException, "get_json_schema", return_value={})

    src = MockSource(streams=[s1, s2, s3])
    mocker.patch.object(MockSource, "stop_sync_on_stream_failure", return_value=True)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            _configured_stream(s1, SyncMode.full_refresh),
            _configured_stream(s2, SyncMode.full_refresh),
            _configured_stream(s3, SyncMode.full_refresh),
        ]
    )

    expected = _fix_emitted_at(
        [
            _as_stream_status("s1", AirbyteStreamStatus.STARTED),
            _as_stream_status("s1", AirbyteStreamStatus.RUNNING),
            *_as_records("s1", stream_output),
            _as_stream_status("s1", AirbyteStreamStatus.COMPLETE),
            _as_stream_status("lamentations", AirbyteStreamStatus.STARTED),
            _as_stream_status("lamentations", AirbyteStreamStatus.INCOMPLETE),
            _as_error_trace("lamentations", "I was born only to crash like Icarus", None, FailureType.system_error, None),
        ]
    )

    with pytest.raises(AirbyteTracedException) as exc:
        messages = [_remove_stack_trace(message) for message in src.read(logger, {}, catalog)]
        messages = _fix_emitted_at(messages)

        assert messages == expected

    assert "lamentations" in exc.value.message
    assert exc.value.failure_type == FailureType.config_error


def _remove_stack_trace(message: AirbyteMessage) -> AirbyteMessage:
    """
    Helper method that removes the stack trace from Airbyte trace messages to make asserting against expected records easier
    """
    if message.trace and message.trace.error and message.trace.error.stack_trace:
        message.trace.error.stack_trace = None
    return message
