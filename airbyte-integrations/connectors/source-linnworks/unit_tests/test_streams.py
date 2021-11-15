#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from source_linnworks.streams import LinnworksStream, Location, StockItems, StockLocations


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(LinnworksStream, "path", "v0/example_endpoint")
    mocker.patch.object(LinnworksStream, "primary_key", "test_primary_key")
    mocker.patch.object(LinnworksStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = LinnworksStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = LinnworksStream()
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, requests_mock):
    stream = LinnworksStream()
    requests_mock.get(
        "https://dummy",
        json={
            "Foo": "foo",
            "Bar": {
                "Baz": "baz",
            },
        },
    )
    resp = requests.get("https://dummy")
    inputs = {"response": resp}
    expected_parsed_object = {"Bar": {"Baz": "baz"}, "Foo": "foo"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_http_method(patch_base_class):
    stream = LinnworksStream()
    expected_method = "POST"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("header_name", "header_value", "expected"),
    [
        ("Retry-After", "123", 123),
        ("Retry-After", "-123", -123),
    ],
)
def test_backoff_time(patch_base_class, requests_mock, header_name, header_value, expected):
    stream = LinnworksStream()
    requests_mock.get("https://dummy", headers={header_name: header_value}, status_code=429)
    result = stream.backoff_time(requests.get("https://dummy"))
    assert result == expected


def test_stock_locations_read_records(mocker):
    fake_stock_locations = [
        {"StockLocationId": 1},
        {"StockLocationId": 2},
    ]

    mocker.patch.object(LinnworksStream, "read_records", lambda *args: iter(fake_stock_locations))
    mocker.patch.object(Location, "read_records", lambda *args: iter([{"FakeLocationFor": args[-1]}]))

    source = StockLocations()
    records = source.read_records(SyncMode.full_refresh)

    assert list(records) == [
        {"StockLocationId": 1, "location": {"FakeLocationFor": {"pkStockLocationId": 1}}},
        {"StockLocationId": 2, "location": {"FakeLocationFor": {"pkStockLocationId": 2}}},
    ]


@pytest.mark.parametrize(
    ("query", "item_count", "expected"),
    [
        ("", 0, None),
        ("?entriesPerPage=100&pageNumber=1", 100, {"entriesPerPage": 100, "pageNumber": 2}),
        ("?entriesPerPage=200&pageNumber=2", 100, None),
    ],
)
def test_stock_items_next_page_token(mocker, requests_mock, query, item_count, expected):
    url = f"http://dummy{query}"
    requests_mock.get(url, json=[None] * item_count)
    response = requests.get(url)

    source = StockItems()
    next_page_token = source.next_page_token(response)

    assert next_page_token == expected


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (200, ["the_response"]),
        (400, []),
        (500, []),
    ],
)
def test_stock_items_parse_response(mocker, requests_mock, status_code, expected):
    requests_mock.get("https://dummy", json="the_response", status_code=status_code)
    response = requests.get("https://dummy")

    source = StockItems()
    parsed_response = source.parse_response(response)

    if status_code not in [200, 400]:
        with pytest.raises(requests.exceptions.HTTPError):
            list(parsed_response)
    else:
        assert list(parsed_response) == expected


@pytest.mark.parametrize(
    ("next_page_token", "expected"),
    [
        (None, False),
        ({"NextPageTokenKey": "NextPageTokenValue"}, True),
    ],
)
def test_stock_items_request_params(mocker, requests_mock, next_page_token, expected):
    source = StockItems()
    params = source.request_params(None, None, next_page_token)

    assert ("NextPageTokenKey" in params) == expected
    if next_page_token:
        assert next_page_token.items() <= params.items()
