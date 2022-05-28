#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time

import pytest as pytest
from airbyte_cdk.models import SyncMode
from source_mailgun.source import Domains, Events, IncrementalMailgunStream

from . import TEST_CONFIG


@pytest.mark.parametrize(
    "stream, cursor_field",
    [
        (IncrementalMailgunStream(TEST_CONFIG), []),
        (Domains(TEST_CONFIG), []),
        (Events(TEST_CONFIG), "timestamp"),
    ],
)
def test_cursor_field(stream, cursor_field):
    assert stream.cursor_field == cursor_field


@pytest.mark.parametrize(
    "stream, current_stream_state, latest_record, expected_state",
    [
        (IncrementalMailgunStream(TEST_CONFIG), None, None, {}),
        (Events(TEST_CONFIG), {"timestamp": 1000}, {"timestamp": 2000}, {"timestamp": 2000}),
        (Events(TEST_CONFIG), {"timestamp": 2000}, {"timestamp": 1000}, {"timestamp": 2000}),
    ],
)
def test_get_updated_state(stream, current_stream_state, latest_record, expected_state):
    inputs = {"current_stream_state": current_stream_state, "latest_record": latest_record}
    assert stream.get_updated_state(**inputs) == expected_state


def test_get_updated_state_events_default_timestamp():
    state = Events(TEST_CONFIG).get_updated_state(current_stream_state={}, latest_record={})
    assert state["timestamp"] == pytest.approx(time.time(), 60 * 60)


@pytest.mark.parametrize(
    "stream, inputs, expected_stream_slice",
    [
        (IncrementalMailgunStream(TEST_CONFIG), {"sync_mode": SyncMode.incremental}, None),
        (Events(TEST_CONFIG), {"stream_state": {"timestamp": 1000000}}, {"begin": 1000000, "end": 1086400}),
    ],
)
def test_stream_slices(stream, inputs, expected_stream_slice):
    slices = iter(stream.stream_slices(**inputs))
    assert next(slices) == expected_stream_slice


@pytest.mark.parametrize(
    "stream, support_incremental",
    [
        (Domains(TEST_CONFIG), False),
        (Events(TEST_CONFIG), True),
    ],
)
def test_supports_incremental(stream, support_incremental):
    assert stream.supports_incremental == support_incremental


@pytest.mark.parametrize(
    "stream, source_defined_cursor",
    [
        (Domains(TEST_CONFIG), True),
        (Events(TEST_CONFIG), True),
    ],
)
def test_source_defined_cursor(stream, source_defined_cursor):
    assert stream.source_defined_cursor == source_defined_cursor


@pytest.mark.parametrize(
    "stream, state_checkpoint_interval",
    [
        (Domains(TEST_CONFIG), None),
        (Events(TEST_CONFIG), None),
    ],
)
def test_stream_checkpoint_interval(stream, state_checkpoint_interval):
    assert stream.state_checkpoint_interval == state_checkpoint_interval
