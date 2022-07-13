#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_exchange_rate_api.source import ExchangeRateApiStream, LatestRates


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ExchangeRateApiStream, "path", "v0/example_endpoint")
    mocker.patch.object(ExchangeRateApiStream, "primary_key", "test_primary_key")
    mocker.patch.object(ExchangeRateApiStream, "__abstractmethods__", set())

    return {
        "config": {
            "base": "USD",
            "symbols": ["USD", "EUR"],
            "start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d")
        }
    }


def test_request_params(patch_base_class):
    assert LatestRates(config=patch_base_class["config"]).request_params(
        stream_state=MagicMock(),
        stream_slice=MagicMock(),
        next_page_token=MagicMock()
    ) == {"base": "USD", "symbols": ["USD", "EUR"]}


def test_next_page_token(patch_base_class):
    stream = ExchangeRateApiStream(config=patch_base_class["config"])
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = ExchangeRateApiStream(config=patch_base_class["config"])
    response = MagicMock()
    response.json.return_value = {"record": "expected record"}
    inputs = {"response": response}
    expected_parsed_object = {"record": "expected record"}
    assert next(iter(stream.parse_response(**inputs))) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = ExchangeRateApiStream(config=patch_base_class["config"])
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = ExchangeRateApiStream(config=patch_base_class["config"])
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = ExchangeRateApiStream(config=patch_base_class["config"])
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = ExchangeRateApiStream(config=patch_base_class["config"])
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
