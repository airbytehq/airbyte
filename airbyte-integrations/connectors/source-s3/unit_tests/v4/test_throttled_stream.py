#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""Unit tests for source_s3.v4.throttled_stream.ThrottledFileBasedStream."""

import logging
from typing import Iterable, List, Mapping, Optional
from unittest.mock import Mock, patch

import pytest
from source_s3.v4.throttled_stream import ThrottledFileBasedStream

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import FileBasedErrorsCollector
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger


def _state(value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="s", namespace=None),
                stream_state={"cursor": value},
            ),
        ),
    )


def _record(value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.RECORD,
        record=AirbyteRecordMessage(stream="s", data={"value": value}, emitted_at=0),
    )


def _cursor_value(message: AirbyteMessage) -> int:
    assert message.state is not None
    assert message.state.stream is not None
    cursor = message.state.stream.stream_state["cursor"]
    assert isinstance(cursor, int)
    return cursor


def _record_value(message: AirbyteMessage) -> int:
    assert message.record is not None
    value = message.record.data["value"]
    assert isinstance(value, int)
    return value


def _summary(messages: List[AirbyteMessage]) -> List[tuple[MessageType, int]]:
    return [(message.type, _cursor_value(message) if message.type == MessageType.STATE else _record_value(message)) for message in messages]


class _TestStream(ThrottledFileBasedStream):
    """ThrottledFileBasedStream subclass that pipes a scripted message
    sequence through the throttling logic, bypassing the parent's heavy
    `read()` setup so tests stay focused on the throttle behaviour.
    """

    def __init__(self, scripted_messages: List[AirbyteMessage]) -> None:
        # NOTE: deliberately do NOT call super().__init__ — we are exercising
        # only the read() filter, not the file-based stream construction.
        self._scripted_messages = scripted_messages
        # Inherited class-level throttle (600 s) is preserved.

    def _scripted_super_read(self) -> Iterable[AirbyteMessage]:
        return iter(self._scripted_messages)


def _run(messages: List[AirbyteMessage], times: List[float]) -> List[AirbyteMessage]:
    """Drive `_TestStream.read()` with the scripted message list and a fixed
    sequence of `time.time()` return values."""
    stream = _TestStream(messages)
    # Substitute the parent's read() for our scripted source.
    with patch(
        "source_s3.v4.throttled_stream.DefaultFileBasedStream.read",
        lambda self, *a, **kw: stream._scripted_super_read(),
    ):
        with patch("source_s3.v4.throttled_stream.time.time", side_effect=times):
            return list(stream.read())


def test_first_state_is_emitted_immediately():
    out = _run([_record(1), _state(1), _record(2)], times=[700.0])
    assert _summary(out) == [
        (MessageType.RECORD, 1),
        (MessageType.STATE, 1),
        (MessageType.RECORD, 2),
    ]


def test_subsequent_states_inside_window_are_suppressed_and_final_emit_fires():
    """Several STATEs in quick succession: at most one STATE is emitted
    mid-stream; the latest suppressed STATE is force-emitted at the end."""
    out = _run(
        [
            _record(1),
            _state(1),  # t=0 — held (delta < 600)
            _record(2),
            _state(2),  # t=10 — held (replaces #1)
            _record(3),
            _state(3),  # t=20 — held (replaces #2)
        ],
        times=[0.0, 10.0, 20.0],
    )
    assert _summary(out) == [
        (MessageType.RECORD, 1),
        (MessageType.RECORD, 2),
        (MessageType.RECORD, 3),
        (MessageType.STATE, 3),
    ]


def test_state_outside_window_is_emitted_and_resets_clock():
    """A STATE that falls outside the throttle window from the previous emit
    is emitted, and the clock resets."""
    out = _run(
        [
            _state(1),  # t=605 (delta=605>600 vs last_emit_at=0) → emit
            _state(2),  # t=610 (delta=5<600) → hold
            _state(3),  # t=1300 (delta=690>600 vs last_emit_at=605) → emit
            _state(4),  # t=1305 → hold
        ],
        times=[605.0, 610.0, 1300.0, 1305.0],
    )
    state_msgs = [m for m in out if m.type == MessageType.STATE]
    cursors = [_cursor_value(m) for m in state_msgs]
    # 1 and 3 emitted mid-stream; 4 force-emitted at end (replaces held 2).
    assert cursors == [1, 3, 4]


def test_non_state_messages_pass_through_untouched():
    out = _run([_record(1), _record(2), _record(3)], times=[])
    types = [m.type for m in out]
    assert types == [MessageType.RECORD, MessageType.RECORD, MessageType.RECORD]


def test_no_states_means_no_final_emit():
    """Without any STATE in the stream, the wrapper should not synthesize one
    at the end."""
    out = _run([_record(1)], times=[])
    assert all(m.type == MessageType.RECORD for m in out)


def test_default_throttle_is_600_seconds():
    """Guards against accidental default changes — 600 s matches the
    ConcurrentPerPartitionCursor throttle cadence (oncall #7856)."""
    assert ThrottledFileBasedStream.state_emission_throttle_seconds == 600.0


def test_pending_state_is_not_flushed_when_parent_read_fails():
    stream = _TestStream([])

    def parent_read(self: ThrottledFileBasedStream, *args: object, **kwargs: object) -> Iterable[AirbyteMessage]:
        yield _state(1)
        yield _state(2)
        raise RuntimeError("boom")

    with patch("source_s3.v4.throttled_stream.DefaultFileBasedStream.read", parent_read):
        with patch("source_s3.v4.throttled_stream.time.time", side_effect=[700.0, 710.0]):
            iterator = stream.read()
            assert _cursor_value(next(iterator)) == 1
            with pytest.raises(RuntimeError, match="boom"):
                next(iterator)


class _InlineStateCursor:
    def __init__(self) -> None:
        self._state: dict[str, object] = {}

    def set_initial_state(self, stream_state: Mapping[str, object]) -> None:
        self._state = dict(stream_state)

    def get_state(self) -> Mapping[str, object]:
        return self._state

    def get_stream_state(self) -> Mapping[str, object]:
        return self._state

    def set_cursor(self, value: int) -> None:
        self._state = {"cursor": value}


class _InlineStateParentStream(ThrottledFileBasedStream):
    _schema: Mapping[str, object] = {
        "type": "object",
        "properties": {
            "value": {"type": "integer"},
            "_ab_source_file_last_modified": {"type": "string"},
            "_ab_source_file_url": {"type": "string"},
        },
    }

    def __init__(self) -> None:
        self._test_cursor = _InlineStateCursor()
        super().__init__(
            config=FileBasedStreamConfig(name="s", validation_policy="Emit Record", format=CsvFormat()),
            catalog_schema=self._schema,
            stream_reader=Mock(),
            availability_strategy=Mock(),
            discovery_policy=Mock(),
            parsers={},
            validation_policy=Mock(),
            errors_collector=FileBasedErrorsCollector(),
            cursor=self._test_cursor,
        )

    def compute_slices(self) -> Iterable[Mapping[str, int]]:
        return [{"cursor": 1}, {"cursor": 2}]

    def get_json_schema(self) -> Mapping[str, object]:
        return self._schema

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, int]] = None,
        stream_state: Optional[Mapping[str, object]] = None,
    ) -> Iterable[StreamData]:
        assert stream_slice is not None
        value = stream_slice["cursor"]
        self._test_cursor.set_cursor(value)
        yield _record(value)


class _StateManager:
    def __init__(self) -> None:
        self._state: Mapping[str, object] = {}

    def update_state_for_stream(self, stream_name: str, namespace: Optional[str], stream_state: Mapping[str, object]) -> None:
        self._state = stream_state

    def create_state_message(self, stream_name: str, namespace: Optional[str]) -> AirbyteMessage:
        return _state(int(self._state["cursor"]))


def test_cdk_parent_read_yields_inline_state_messages_throttled_by_subclass():
    stream = _InlineStateParentStream()
    state_manager = _StateManager()
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="s",
            json_schema={},
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        cursor_field=["_ab_source_file_last_modified"],
        destination_sync_mode=DestinationSyncMode.append,
    )

    with patch("source_s3.v4.throttled_stream.time.time", side_effect=[700.0, 710.0]):
        out = list(
            stream.read(
                configured_stream=configured_stream,
                logger=logging.getLogger("test"),
                slice_logger=DebugSliceLogger(),
                stream_state={},
                state_manager=state_manager,
                internal_config=InternalConfig(),
            )
        )

    assert _summary(out) == [
        (MessageType.RECORD, 1),
        (MessageType.STATE, 1),
        (MessageType.RECORD, 2),
        (MessageType.STATE, 2),
    ]
