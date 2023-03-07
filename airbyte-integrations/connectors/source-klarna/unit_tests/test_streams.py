#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator
from source_klarna.source import KlarnaStream, Payouts, Transactions


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(KlarnaStream, "path", "v0/example_endpoint")
    mocker.patch.object(KlarnaStream, "primary_key", "test_primary_key")
    mocker.patch.object(KlarnaStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, klarna_stream):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"offset": 0, "size": 500}
    assert klarna_stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    "total,count,offset,next_,expected_params",
    [
        (9, 4, 0, "https://api.playground.klarna.com/settlements/v1/payouts?offset=4&size=4", {"offset": ["4"], "size": ["4"]}),
        (9, 4, 4, "https://api.playground.klarna.com/settlements/v1/payouts?offset=48&size=4", {"offset": ["48"], "size": ["4"]}),
    ],
)
def test_next_page_token(patch_base_class, klarna_stream, total, count, offset, next_, expected_params):
    response_mock = MagicMock()
    response_mock.json.return_value = {
        "pagination": {
            "total": total,
            "count": count,
            "offset": offset,
            "next": next_,
        }
    }
    inputs = {"response": response_mock}
    assert klarna_stream.next_page_token(**inputs) == expected_params


@pytest.mark.parametrize(
    ("specific_klarna_stream", "response"),
    [
        (Payouts, {"payouts": [{}]}),
        (Transactions, {"transactions": [{}]}),
    ],
)
def test_parse_response(patch_base_class, klarna_config, specific_klarna_stream, response):
    mock_response = MagicMock()
    mock_response.json.return_value = response
    inputs = {"response": mock_response, "stream_state": {}}
    stream = specific_klarna_stream(authenticator=BasicHttpAuthenticator("", ""), **klarna_config)
    assert next(stream.parse_response(**inputs)) == {}


def test_request_headers(patch_base_class, klarna_stream):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert klarna_stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class, klarna_stream):
    expected_method = "GET"
    assert klarna_stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry, klarna_stream):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    assert klarna_stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, klarna_stream):
    response_mock = MagicMock()
    expected_backoff_time = None
    assert klarna_stream.backoff_time(response_mock) == expected_backoff_time
