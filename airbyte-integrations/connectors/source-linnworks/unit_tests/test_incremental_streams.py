#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from unittest.mock import MagicMock

import pendulum
import pytest
import requests
import vcr
from source_linnworks.streams import IncrementalLinnworksStream, ProcessedOrderDetails, ProcessedOrders

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams.http.http import HttpSubStream


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


def date(*args):
    return pendulum.datetime(*args).isoformat()


@pytest.mark.parametrize(
    ("now", "stream_state", "slice_count", "expected_from_date", "expected_to_date"),
    [
        (None, None, 24, date(2050, 1, 1), date(2050, 1, 2)),
        (date(2050, 1, 2), None, 48, date(2050, 1, 1), date(2050, 1, 3)),
        (None, {"dProcessedOn": date(2050, 1, 4)}, 1, date(2050, 1, 4), date(2050, 1, 4)),
        (
            date(2050, 1, 5),
            {"dProcessedOn": date(2050, 1, 4)},
            48,
            date(2050, 1, 4),
            date(2050, 1, 6),
        ),
        (
            # Yearly
            date(2052, 1, 1),
            {"dProcessedOn": date(2050, 1, 1)},
            25,
            date(2050, 1, 1),
            date(2052, 1, 2),
        ),
        (
            # Monthly
            date(2050, 4, 1),
            {"dProcessedOn": date(2050, 1, 1)},
            13,
            date(2050, 1, 1),
            date(2050, 4, 2),
        ),
        (
            # Weekly
            date(2050, 1, 31),
            {"dProcessedOn": date(2050, 1, 1)},
            5,
            date(2050, 1, 1),
            date(2050, 2, 1),
        ),
        (
            # Daily
            date(2050, 1, 1, 23, 59, 59),
            {"dProcessedOn": date(2050, 1, 1)},
            24,
            date(2050, 1, 1),
            date(2050, 1, 2),
        ),
    ],
)
def test_processed_orders_stream_slices(patch_incremental_base_class, now, stream_state, slice_count, expected_from_date, expected_to_date):
    start_date = date(2050, 1, 1)
    pendulum.set_test_now(pendulum.parse(now if now else start_date))

    stream = ProcessedOrders(start_date=start_date)
    stream_slices = list(stream.stream_slices(stream_state))

    assert len(stream_slices) == slice_count
    assert stream_slices[0]["FromDate"] == expected_from_date
    assert stream_slices[-1]["ToDate"] == expected_to_date


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


def test_processed_orders_request_cache(patch_incremental_base_class, mocker):
    remove = MagicMock()
    use_cassette = MagicMock()

    mocker.patch.object(os, "remove", remove)
    mocker.patch.object(vcr, "use_cassette", use_cassette)

    stream = ProcessedOrders()
    stream.request_cache()

    remove.assert_called_with(stream.cache_filename)
    use_cassette.assert_called_with(
        stream.cache_filename,
        record_mode="new_episodes",
        serializer="yaml",
        match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    )


@pytest.mark.parametrize(
    ("count", "stream_state"),
    [
        (5, None),
        (205, None),
        (5, {"ProcessedDateTime": "a-date"}),
    ],
)
def test_processed_order_details_stream_slices(patch_incremental_base_class, mocker, count, stream_state):
    parent_stream_slices = MagicMock(return_value=[{"parent": {"pkOrderID": str(n)}} for n in range(count)])
    mocker.patch.object(HttpSubStream, "stream_slices", parent_stream_slices)

    stream = ProcessedOrderDetails()
    expected_slices = [[str(m) for m in range(count)[i : i + stream.page_size]] for i in range(0, count, stream.page_size)]

    stream_slices = stream.stream_slices(sync_mode=SyncMode.full_refresh, stream_state=stream_state)

    assert list(stream_slices) == list(expected_slices)


def test_processed_order_details_request_body_data(patch_incremental_base_class):
    stream = ProcessedOrderDetails()
    request_body_data = stream.request_body_data(None, ["abc", "def", "ghi"])

    assert request_body_data == {"pkOrderIds": '["abc","def","ghi"]'}
