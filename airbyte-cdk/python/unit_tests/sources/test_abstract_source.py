#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple, Union
from unittest.mock import call

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

logger = logging.getLogger("airbyte")


class MockSource(AbstractSource):
    def __init__(
        self,
        check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None,
        streams: List[Stream] = None,
    ):
        self._streams = streams
        self.check_lambda = check_lambda

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        if self.check_lambda:
            return self.check_lambda()
        return (False, "Missing callable.")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not self._streams:
            raise Exception("Stream is not set")
        return self._streams


def test_successful_check():
    """Tests that if a source returns TRUE for the connection check the appropriate connectionStatus success message is returned"""
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert expected == MockSource(check_lambda=lambda: (True, None)).check(logger, {})


def test_failed_check():
    """Tests that if a source returns FALSE for the connection check the appropriate connectionStatus failure message is returned"""
    expected = AirbyteConnectionStatus(status=Status.FAILED, message="'womp womp'")
    assert expected == MockSource(check_lambda=lambda: (False, "womp womp")).check(logger, {})


def test_raising_check():
    """Tests that if a source raises an unexpected exception the appropriate connectionStatus failure message is returned."""
    expected = AirbyteConnectionStatus(status=Status.FAILED, message="Exception('this should fail')")
    assert expected == MockSource(check_lambda=lambda: exec('raise Exception("this should fail")')).check(logger, {})


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

    expected = _as_records("s1", stream_output) + _as_records("s2", stream_output)
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

    expected = [*_as_records("s1", slices), *_as_records("s2", slices)]

    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert expected == messages


def _state(state_data: Dict[str, Any]):
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state_data))


class TestIncrementalRead:
    def test_with_state_attribute(self, mocker):
        """Test correct state passing for the streams that have a state attribute"""
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]
        old_state = {"cursor": "old_value"}
        new_state = {"cursor": "new_value"}
        s1 = MockStreamWithState(
            [
                (
                    {"sync_mode": SyncMode.incremental, "stream_state": old_state},
                    stream_output,
                )
            ],
            name="s1",
        )
        s2 = MockStreamWithState(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s2",
        )
        mocker.patch.object(MockStreamWithState, "get_updated_state", return_value={})
        state_property = mocker.patch.object(
            MockStreamWithState,
            "state",
            new_callable=mocker.PropertyMock,
            return_value=new_state,
        )
        mocker.patch.object(MockStreamWithState, "get_json_schema", return_value={})
        src = MockSource(streams=[s1, s2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.incremental),
                _configured_stream(s2, SyncMode.incremental),
            ]
        )

        expected = [
            _as_record("s1", stream_output[0]),
            _as_record("s1", stream_output[1]),
            _state({"s1": new_state}),
            _as_record("s2", stream_output[0]),
            _as_record("s2", stream_output[1]),
            _state({"s1": new_state, "s2": new_state}),
        ]
        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state={"s1": old_state})))

        assert expected == messages
        assert state_property.mock_calls == [
            call(old_state),  # set state for s1
            call(),  # get state in the end of slice for s1
            call(),  # get state in the end of slice for s2
        ]

    def test_with_checkpoint_interval(self, mocker):
        """Tests that an incremental read which doesn't specify a checkpoint interval outputs a STATE message
        after reading N records within a stream.
        """
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]
        s1 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s1",
        )
        s2 = MockStream(
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

        src = MockSource(streams=[s1, s2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.incremental),
                _configured_stream(s2, SyncMode.incremental),
            ]
        )

        expected = [
            _as_record("s1", stream_output[0]),
            _state({"s1": state}),
            _as_record("s1", stream_output[1]),
            _state({"s1": state}),
            _state({"s1": state}),
            _as_record("s2", stream_output[0]),
            _state({"s1": state, "s2": state}),
            _as_record("s2", stream_output[1]),
            _state({"s1": state, "s2": state}),
            _state({"s1": state, "s2": state}),
        ]
        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

        assert expected == messages

    def test_with_no_interval(self, mocker):
        """Tests that an incremental read which doesn't specify a checkpoint interval outputs
        a STATE message only after fully reading the stream and does not output any STATE messages during syncing the stream.
        """
        stream_output = [{"k1": "v1"}, {"k2": "v2"}]
        s1 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s1",
        )
        s2 = MockStream(
            [({"sync_mode": SyncMode.incremental, "stream_state": {}}, stream_output)],
            name="s2",
        )
        state = {"cursor": "value"}
        mocker.patch.object(MockStream, "get_updated_state", return_value=state)
        mocker.patch.object(MockStream, "supports_incremental", return_value=True)
        mocker.patch.object(MockStream, "get_json_schema", return_value={})

        src = MockSource(streams=[s1, s2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.incremental),
                _configured_stream(s2, SyncMode.incremental),
            ]
        )

        expected = [
            *_as_records("s1", stream_output),
            _state({"s1": state}),
            *_as_records("s2", stream_output),
            _state({"s1": state, "s2": state}),
        ]

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

        assert expected == messages

    def test_with_slices(self, mocker):
        """Tests that an incremental read which uses slices outputs each record in the slice followed by a STATE message, for each slice"""
        slices = [{"1": "1"}, {"2": "2"}]
        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]
        s1 = MockStream(
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
        s2 = MockStream(
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

        src = MockSource(streams=[s1, s2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.incremental),
                _configured_stream(s2, SyncMode.incremental),
            ]
        )

        expected = [
            # stream 1 slice 1
            *_as_records("s1", stream_output),
            _state({"s1": state}),
            # stream 1 slice 2
            *_as_records("s1", stream_output),
            _state({"s1": state}),
            # stream 2 slice 1
            *_as_records("s2", stream_output),
            _state({"s1": state, "s2": state}),
            # stream 2 slice 2
            *_as_records("s2", stream_output),
            _state({"s1": state, "s2": state}),
        ]

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

        assert expected == messages

    def test_no_slices(self, mocker):
        """
        Tests that an incremental read returns at least one state messages even if no records were read:
            1. outputs a state message after reading the entire stream
        """
        slices = []
        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]
        state = {"cursor": "value"}
        s1 = MockStreamWithState(
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
        s2 = MockStreamWithState(
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

        src = MockSource(streams=[s1, s2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.incremental),
                _configured_stream(s2, SyncMode.incremental),
            ]
        )

        expected = [
            _state({"s1": state}),
            _state({"s1": state, "s2": state}),
        ]

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

        print(f"expected:\n{expected}")
        print(f"messages:\n{messages}")
        assert expected == messages

    def test_with_slices_and_interval(self, mocker):
        """
        Tests that an incremental read which uses slices and a checkpoint interval:
            1. outputs all records
            2. outputs a state message every N records (N=checkpoint_interval)
            3. outputs a state message after reading the entire slice
        """
        slices = [{"1": "1"}, {"2": "2"}]
        stream_output = [{"k1": "v1"}, {"k2": "v2"}, {"k3": "v3"}]
        s1 = MockStream(
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
        s2 = MockStream(
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

        src = MockSource(streams=[s1, s2])
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                _configured_stream(s1, SyncMode.incremental),
                _configured_stream(s2, SyncMode.incremental),
            ]
        )

        expected = [
            # stream 1 slice 1
            _as_record("s1", stream_output[0]),
            _as_record("s1", stream_output[1]),
            _state({"s1": state}),
            _as_record("s1", stream_output[2]),
            _state({"s1": state}),
            # stream 1 slice 2
            _as_record("s1", stream_output[0]),
            _as_record("s1", stream_output[1]),
            _state({"s1": state}),
            _as_record("s1", stream_output[2]),
            _state({"s1": state}),
            # stream 2 slice 1
            _as_record("s2", stream_output[0]),
            _as_record("s2", stream_output[1]),
            _state({"s1": state, "s2": state}),
            _as_record("s2", stream_output[2]),
            _state({"s1": state, "s2": state}),
            # stream 2 slice 2
            _as_record("s2", stream_output[0]),
            _as_record("s2", stream_output[1]),
            _state({"s1": state, "s2": state}),
            _as_record("s2", stream_output[2]),
            _state({"s1": state, "s2": state}),
        ]

        messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

        assert expected == messages
