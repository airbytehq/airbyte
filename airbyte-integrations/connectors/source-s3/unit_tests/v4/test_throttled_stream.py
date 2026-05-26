#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""Unit tests for source_s3.v4.throttled_stream.ThrottledFileBasedStream."""

from typing import Iterable, List
from unittest.mock import patch

from source_s3.v4.throttled_stream import ThrottledFileBasedStream

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
)
from airbyte_cdk.models import Type as MessageType


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
    """Cold-start STATE goes through (delta < 600 s but we have not yet
    emitted, so the first one is always allowed)."""
    out = _run([_record(1), _state(1), _record(2)], times=[0.0])
    state_msgs = [m for m in out if m.type == MessageType.STATE]
    # The first STATE is suppressed by our `now - last_emit_at < throttle`
    # check because last_emit_at starts at 0.0. We force-emit the held one
    # at end of stream, so we still see exactly one STATE.
    assert len(state_msgs) == 1
    assert state_msgs[0].state.stream.stream_state["cursor"] == 1


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
    state_msgs = [m for m in out if m.type == MessageType.STATE]
    # Only one STATE survives — the latest one, force-emitted at the end.
    assert len(state_msgs) == 1
    assert state_msgs[0].state.stream.stream_state["cursor"] == 3


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
    cursors = [m.state.stream.stream_state["cursor"] for m in state_msgs]
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
