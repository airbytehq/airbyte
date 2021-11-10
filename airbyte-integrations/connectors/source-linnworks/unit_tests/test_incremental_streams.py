#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_linnworks.streams import IncrementalLinnworksStream, ProcessedOrders


@pytest.fixture
def patch_incremental_base_class(mocker):
    mocker.patch.object(IncrementalLinnworksStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalLinnworksStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalLinnworksStream, "cursor_field", "test_cursor_field")
    mocker.patch.object(IncrementalLinnworksStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    expected_cursor_field = "test_cursor_field"
    assert stream.cursor_field == expected_cursor_field


@pytest.mark.parametrize(
    ("inputs", "expected_state"),
    [
        (
            {
                "current_stream_state": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:56",
                },
                "latest_record": {},
            },
            {"test_cursor_field": "2021-01-01T01:02:34+01:56"},
        ),
        (
            {
                "current_stream_state": {},
                "latest_record": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:56",
                },
            },
            {"test_cursor_field": "2021-01-01T01:02:34+01:56"},
        ),
        (
            {
                "current_stream_state": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:56",
                },
                "latest_record": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:57",
                },
            },
            {"test_cursor_field": "2021-01-01T01:02:34+01:57"},
        ),
    ],
)
def test_get_updated_state(patch_incremental_base_class, inputs, expected_state):
    stream = IncrementalLinnworksStream()
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalLinnworksStream, "cursor_field", "dummy_field")
    stream = IncrementalLinnworksStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


@pytest.mark.parametrize(
    ("now", "stream_state", "expected_from_date", "expected_to_date"),
    [
        (None, None, "2050-01-01T00:00:00+00:00", "2050-01-01T00:00:00+00:00"),
        ("2050-01-02T00:00:00+00:00", None, "2050-01-01T00:00:00+00:00", "2050-01-03T00:00:00+00:00"),
        (None, {"dReceivedDate": "2050-01-04T00:00:00+00:00"}, "2050-01-04T00:00:00+00:00", "2050-01-04T00:00:00+00:00"),
        (
            "2050-01-05T00:00:00+00:00",
            {"dReceivedDate": "2050-01-04T00:00:00+00:00"},
            "2050-01-04T00:00:00+00:00",
            "2050-01-06T00:00:00+00:00",
        ),
    ],
)
def test_processed_orders_stream_slices(patch_incremental_base_class, now, stream_state, expected_from_date, expected_to_date):
    start_date = "2050-01-01T00:00:00+00:00"
    stream = ProcessedOrders(start_date=start_date)

    if now:
        now_date = pendulum.parse(now)
        pendulum.set_test_now(now_date)

    stream_slices = stream.stream_slices(stream_state)

    assert stream_slices[0]["FromDate"] == expected_from_date
    assert stream_slices[0]["ToDate"] == expected_to_date


@pytest.mark.parametrize(
    ("page_number"),
    [
        (None),
        (42),
    ],
)
def test_processed_orders_request_body_data(patch_incremental_base_class, page_number):
    stream_slice = {"FromDate": "FromDateValue", "ToDate": "ToDateValue"}
    next_page_token = {"PageNumber": page_number}

    stream = ProcessedOrders()
    request_body_data = stream.request_body_data(None, stream_slice, next_page_token)
    data = json.loads(request_body_data["request"])

    assert stream_slice.items() < data.items()
    assert next_page_token.items() < data.items()


def test_processed_orders_paged_result(patch_incremental_base_class, requests_mock):
    requests_mock.get("https://dummy", json={"ProcessedOrders": "the_orders"})
    good_response = requests.get("https://dummy")

    requests_mock.get("https://dummy", json={"OtherData": "the_data"})
    bad_response = requests.get("https://dummy")

    stream = ProcessedOrders()
    result = stream.paged_result(good_response)
    assert result == "the_orders"

    with pytest.raises(KeyError, match="'ProcessedOrders'"):
        stream.paged_result(bad_response)


def test_processed_orders_parse_response(patch_incremental_base_class, requests_mock):
    requests_mock.get("https://dummy", json={"ProcessedOrders": {"Data": [1, 2, 3]}})
    good_response = requests.get("https://dummy")

    requests_mock.get("https://dummy", json={"ProcessedOrders": {"OtherData": [1, 2, 3]}})
    bad_response = requests.get("https://dummy")

    stream = ProcessedOrders()
    result = stream.parse_response(good_response)
    assert list(result) == [1, 2, 3]

    with pytest.raises(KeyError, match="'Data'"):
        list(stream.parse_response(bad_response))
