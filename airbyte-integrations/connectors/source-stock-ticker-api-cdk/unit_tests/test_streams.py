#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

from requests import Response, Session

import pytest
from source_stock_ticker_api_cdk.source import StockPrices, SourceStockTickerApiCDK
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException


def test_request_params(patch_base_class, config):
    stream = StockPrices(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"sort": "asc", "apiKey": config["api_key"]}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, config):
    stream = StockPrices(config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, config, response_object):
    stream = StockPrices(config)
    response_mock = MagicMock()
    response_mock.configure_mock(**{"json.return_value": response_object})
    inputs = {"response": response_mock}
    expected_parsed_object = {
        "date": "2023-09-25",
        "stock_ticker": "TCKR",
        "price": 111.11,
    }
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class, config):
    stream = StockPrices(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class, config):
    stream = StockPrices(config)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        (HTTPStatus.FORBIDDEN, False),
        (HTTPStatus.UNPROCESSABLE_ENTITY, False),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry, config):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = StockPrices(config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, config):
    response_mock = MagicMock()
    stream = StockPrices(config)
    expected_backoff_time = 61
    assert stream.backoff_time(response_mock) == expected_backoff_time


@pytest.mark.parametrize(
    "http_status",
    [HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN, HTTPStatus.UNPROCESSABLE_ENTITY],
)
def test_raise_on_http_errors_off(requests_mock, config, http_status):
    # Given: a StockPrices stream with raise_on_http_errors disabled for certain HTTP statuses
    stream = StockPrices(config)
    # When: a response with such status code is returned
    requests_mock.get(f"{stream.url_base}{stream.path()}", status_code=http_status, json={})
    # Then: no HTTP error is raised
    list(stream.read_records(SyncMode.full_refresh))
