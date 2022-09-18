#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_stock_ticker_api_cdk.source import Prices


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Prices, "path", "v0/example_endpoint")
    mocker.patch.object(Prices, "primary_key", "test_primary_key")
    mocker.patch.object(Prices, "__abstractmethods__", set())


@pytest.fixture(name="config")
def config_fixture():
    config = {'api_key': 'api_key', 'stock_ticker': 'stock_ticker'}
    return config


def test_request_params(patch_base_class, config):
    stream = Prices(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {'apiKey': 'api_key', 'limit': 120, 'sort': 'asc'}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, config):
    stream = Prices(config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_request_headers(patch_base_class, config):
    stream = Prices(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class, config):
    stream = Prices(config)
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
def test_should_retry(patch_base_class, http_status, should_retry, config):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = Prices(config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, config):
    response_mock = MagicMock()
    stream = Prices(config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
