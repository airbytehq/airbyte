#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import math
import uuid

import pytest
from pytest import fixture
from source_paystack.streams import IncrementalPaystackStream

START_DATE = "2020-08-01T00:00:00Z"


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalPaystackStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalPaystackStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalPaystackStream, "__abstractmethods__", set())
    mocker.patch.object(IncrementalPaystackStream, "cursor_field", str(uuid.uuid4()))


def test_get_updated_state_uses_timestamp_of_latest_record(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    inputs = {"current_stream_state": {stream.cursor_field: "2021-08-01"}, "latest_record": {stream.cursor_field: "2021-08-02T00:00:00Z"}}

    updated_state = stream.get_updated_state(**inputs)

    assert updated_state == {stream.cursor_field: "2021-08-02T00:00:00Z"}


def test_get_updated_state_returns_current_state_for_old_records(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    current_state = {stream.cursor_field: "2021-08-03"}
    inputs = {"current_stream_state": current_state, "latest_record": {stream.cursor_field: "2021-08-02T00:00:00Z"}}

    updated_state = stream.get_updated_state(**inputs)

    assert updated_state == current_state


def test_get_updated_state_uses_timestamp_of_latest_record_when_no_current_state_exists(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    inputs = {"current_stream_state": {}, "latest_record": {stream.cursor_field: "2021-08-02T00:00:00Z"}}

    updated_state = stream.get_updated_state(**inputs)

    assert updated_state == {stream.cursor_field: "2021-08-02T00:00:00Z"}


def test_request_params_includes_incremental_start_point(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    inputs = {
        "stream_slice": None,
        "next_page_token": {"page": 37},
        "stream_state": {stream.cursor_field: "2021-09-02"},
    }

    params = stream.request_params(**inputs)

    assert params == {"perPage": 200, "page": 37, "from": "2021-09-02T00:00:00Z"}


@pytest.mark.parametrize(
    "lookback_window_days, current_state, expected, message",
    [
        (None, "2021-08-30", "2021-08-30T00:00:00Z", "if lookback_window_days is not set should not affect cursor value"),
        (0, "2021-08-30", "2021-08-30T00:00:00Z", "if lookback_window_days is not set should not affect cursor value"),
        (10, "2021-08-30", "2021-08-20T00:00:00Z", "Should calculate cursor value as expected"),
        (-10, "2021-08-30", "2021-08-20T00:00:00Z", "Should not care for the sign, use the module"),
    ],
)
def test_request_params_incremental_start_point_applies_lookback_window(
    patch_incremental_base_class, lookback_window_days, current_state, expected, message
):
    stream = IncrementalPaystackStream(start_date=START_DATE, lookback_window_days=lookback_window_days)
    inputs = {
        "stream_slice": None,
        "next_page_token": None,
        "stream_state": {stream.cursor_field: current_state},
    }

    params = stream.request_params(**inputs)

    assert params["perPage"] == 200
    assert params["from"] == expected, message


def test_request_params_incremental_start_point_defaults_to_start_date(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    inputs = {"stream_slice": None, "next_page_token": None, "stream_state": None}

    params = stream.request_params(**inputs)

    assert params == {"perPage": 200, "from": "2020-08-01T00:00:00Z"}


def test_supports_incremental(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalPaystackStream(start_date=START_DATE)
    assert stream.state_checkpoint_interval == math.inf
