#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import logging
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.streams import Stream

logger = logging.getLogger("airbyte")
GLOBAL_EMITTED_AT = 1


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

    def __init__(self, inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Iterable[Mapping[str, Any]]]], name: str, state):
        super().__init__(inputs_and_mocked_outputs, name)
        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        pass


class MockSource(DeclarativeSource):
    def __init__(self, streams):
        self._streams = streams

    @property
    def connection_checker(self) -> ConnectionChecker:
        pass

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


class TestIncrementalRead:
    def test_with_slices_and_interval(self, mocker):
        """
        Tests that an incremental read which uses slices and a checkpoint interval:
            1. outputs all records
            2. outputs a state message every N records (N=checkpoint_interval)
            3. outputs a state message after reading the entire slice
        """
        slices = [{"1": "1"}, {"2": "2"}]
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

        mocker.patch.object(MockStreamWithState, "get_updated_state", return_value=state)
        mocker.patch.object(MockStreamWithState, "supports_incremental", return_value=True)
        mocker.patch.object(MockStreamWithState, "get_json_schema", return_value={})
        mocker.patch.object(MockStreamWithState, "stream_slices", return_value=slices)
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

    def test_with_empty_slices(self, mocker):
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

        assert expected == messages


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


def _state(state_data: Dict[str, Any]):
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state_data))
