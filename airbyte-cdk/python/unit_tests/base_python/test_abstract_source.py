from collections import defaultdict
from typing import Mapping, Any, List, Tuple, Optional, Callable, Union, Iterable, Dict

import pytest

from airbyte_cdk import AirbyteConnectionStatus, Status, SyncMode, AirbyteStream, AirbyteCatalog, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, \
    AirbyteMessage, Type, AirbyteRecordMessage
from airbyte_cdk.base_python import AbstractSource, Stream, AirbyteLogger
from airbyte_cdk.models import DestinationSyncMode, AirbyteStateMessage


class MockSource(AbstractSource):
    def __init__(self, check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None, streams: List[Stream] = None):
        self._streams = streams
        self.check_lambda = check_lambda

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return self.check_lambda()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


@pytest.fixture
def logger() -> AirbyteLogger:
    return AirbyteLogger()


def test_successful_check():
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert expected == MockSource(check_lambda=lambda: (True, None)).check(logger, {})


def test_failed_check():
    expected = AirbyteConnectionStatus(status=Status.FAILED, message="womp womp")
    assert expected == MockSource(check_lambda=lambda: (False, "womp womp")).check(logger, {})


def test_raising_check():
    expected = AirbyteConnectionStatus(status=Status.FAILED, message=f"{Exception('this should fail')}")
    assert expected == MockSource(check_lambda=lambda: exec('raise Exception("this should fail")')).check(logger, {})


class MockStream(Stream):
    def __init__(
            self,
            inputs_and_mocked_outputs: List[Tuple[Mapping[str, Any], Iterable[Mapping[str, Any]]]] = None,
            name: str = None
    ):
        self._inputs_and_mocked_outputs = inputs_and_mocked_outputs
        self._name = name

    @property
    def name(self):
        return self._name

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
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


def test_discover(mocker):
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
    mocker.patch.object(stream1, 'as_airbyte_stream', return_value=airbyte_stream1)
    mocker.patch.object(stream2, 'as_airbyte_stream', return_value=airbyte_stream2)

    expected = AirbyteCatalog(streams=[airbyte_stream1, airbyte_stream2])
    src = MockSource(check_lambda=lambda: (True, None), streams=[stream1, stream2])

    assert expected == src.discover(logger, {})


# TODO not implemented yet
# def test_read_nonexistent_stream_raises_exception():
#     pass

GLOBAL_EMITTED_AT = 1


def _as_record(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=GLOBAL_EMITTED_AT))


def _as_records(stream: str, data: List[Dict[str, Any]]) -> List[AirbyteMessage]:
    return [_as_record(stream, datum) for datum in data]


def _configured_stream(stream: Stream, sync_mode: SyncMode):
    return ConfiguredAirbyteStream(stream=stream.as_airbyte_stream(), sync_mode=sync_mode, destination_sync_mode=DestinationSyncMode.overwrite)


def _fix_emitted_at(messages: List[AirbyteMessage]) -> List[AirbyteMessage]:
    for msg in messages:
        if msg.type == Type.RECORD:
            msg.record.emitted_at = GLOBAL_EMITTED_AT
    return messages


def test_valid_fullrefresh_read_no_slices(logger, mocker):
    stream_output = [{'k1': 'v1'}, {'k2': 'v2'}]
    s1 = MockStream([({'sync_mode': SyncMode.full_refresh}, stream_output)], name='s1')
    s2 = MockStream([({'sync_mode': SyncMode.full_refresh}, stream_output)], name='s2')

    mocker.patch.object(MockStream, 'get_json_schema', return_value={})

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s1, SyncMode.full_refresh), _configured_stream(s2, SyncMode.full_refresh)])

    expected = _as_records('s1', stream_output) + _as_records('s2', stream_output)
    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert expected == messages


def test_valid_full_refresh_read_with_slices(mocker, logger):
    stream_output = [{'k1': 'v1'}, {'k2': 'v2'}]
    slices = [{'1': '1'}, {'2': '2'}]
    s1 = MockStream(
        [({'sync_mode': SyncMode.full_refresh, 'stream_slice': s}, stream_output) for s in slices],
        name='s1'
    )
    s2 = MockStream(
        [({'sync_mode': SyncMode.full_refresh, 'stream_slice': s}, stream_output) for s in slices],
        name='s2'
    )

    mocker.patch.object(MockStream, 'get_json_schema', return_value={})
    mocker.patch.object(MockStream, 'stream_slices', return_value=slices)

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s1, SyncMode.full_refresh), _configured_stream(s2, SyncMode.full_refresh)])

    expected = _as_records('s1', stream_output) * 2 + _as_records('s2', stream_output) * 2
    messages = _fix_emitted_at(list(src.read(logger, {}, catalog)))

    assert expected == messages


def _state(state_data: Dict[str, Any]):
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state_data))


def test_valid_incremental_read_with_checkpoint_interval(mocker, logger):
    stream_output = [{'k1': 'v1'}, {'k2': 'v2'}]
    s1 = MockStream([({'sync_mode': SyncMode.incremental, 'stream_state': {}}, stream_output)], name='s1')
    s2 = MockStream([({'sync_mode': SyncMode.incremental, 'stream_state': {}}, stream_output)], name='s2')
    state = {'cursor': 'value'}
    mocker.patch.object(MockStream, 'get_updated_state', return_value=state)
    mocker.patch.object(MockStream, 'supports_incremental', return_value=True)
    mocker.patch.object(MockStream, 'get_json_schema', return_value={})
    # Tell the source to output one state message per record
    mocker.patch.object(MockStream, 'state_checkpoint_interval', return_value=1)

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s1, SyncMode.incremental), _configured_stream(s2, SyncMode.incremental)])

    expected = [
        _as_record('s1', stream_output[0]),
        _state({'s1': state}),
        _as_record('s1', stream_output[1]),
        _state({'s1': state}),
        _as_record('s2', stream_output[0]),
        _state({'s1': state, 's2': state}),
        _as_record('s2', stream_output[1]),
        _state({'s1': state, 's2': state})
    ]
    messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

    assert expected == messages


def test_valid_incremental_read_with_no_interval(mocker, logger):
    stream_output = [{'k1': 'v1'}, {'k2': 'v2'}]
    s1 = MockStream([({'sync_mode': SyncMode.incremental, 'stream_state': {}}, stream_output)], name='s1')
    s2 = MockStream([({'sync_mode': SyncMode.incremental, 'stream_state': {}}, stream_output)], name='s2')
    state = {'cursor': 'value'}
    mocker.patch.object(MockStream, 'get_updated_state', return_value=state)
    mocker.patch.object(MockStream, 'supports_incremental', return_value=True)
    mocker.patch.object(MockStream, 'get_json_schema', return_value={})

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s1, SyncMode.incremental), _configured_stream(s2, SyncMode.incremental)])

    expected = [*_as_records('s1', stream_output), _state({'s1': state}), *_as_records('s2', stream_output), _state({'s1': state, 's2': state})]

    messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

    assert expected == messages


def test_valid_incremental_read_with_slices(mocker, logger):
    slices = [{'1': '1'}, {'2': '2'}]
    stream_output = [{'k1': 'v1'}, {'k2': 'v2'}, {'k3': 'v3'}]
    s1 = MockStream(
        [({'sync_mode': SyncMode.incremental, 'stream_slice': s, 'stream_state': mocker.ANY}, stream_output) for s in slices],
        name='s1'
    )
    s2 = MockStream(
        [({'sync_mode': SyncMode.incremental, 'stream_slice': s, 'stream_state': mocker.ANY}, stream_output) for s in slices],
        name='s2'
    )
    state = {'cursor': 'value'}
    mocker.patch.object(MockStream, 'get_updated_state', return_value=state)
    mocker.patch.object(MockStream, 'supports_incremental', return_value=True)
    mocker.patch.object(MockStream, 'get_json_schema', return_value={})
    mocker.patch.object(MockStream, 'stream_slices', return_value=slices)

    src = MockSource(streams=[s1, s2])
    catalog = ConfiguredAirbyteCatalog(streams=[_configured_stream(s1, SyncMode.incremental), _configured_stream(s2, SyncMode.incremental)])

    expected = [
        # stream 1 slice 1
        *_as_records('s1', stream_output),
        _state({'s1': state}),
        # stream 1 slice 2
        *_as_records('s1', stream_output),
        _state({'s1': state}),
        # stream 2 slice 1
        *_as_records('s2', stream_output),
        _state({'s1': state, 's2': state}),
        # stream 2 slice 2
        *_as_records('s2', stream_output),
        _state({'s1': state, 's2': state})
    ]

    messages = _fix_emitted_at(list(src.read(logger, {}, catalog, state=defaultdict(dict))))

    assert expected == messages
