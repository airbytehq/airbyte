#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_fiserv.source import FiservStream

config = {
    "start_date": "2023-08-04",
    "api_key": "api_key",
    "api_secret": "api_secret",
}


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(FiservStream, "path", "v0/example_endpoint")
    mocker.patch.object(FiservStream, "primary_key", "test_primary_key")
    mocker.patch.object(FiservStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = FiservStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = FiservStream(**config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = FiservStream(**config)
    response = MagicMock()
    expected = [
        {
            "id": "hello",
        }
    ]

    response.json.return_value = expected
    inputs = {"response": response}
    assert next(stream.parse_response(**inputs)) == expected[0]


def test_request_headers(patch_base_class):
    stream = FiservStream(**config)
    inputs = {
        "stream_slice": {
            "fromDate": "20230804",
            "toDate": "20230805",
        },
        "stream_state": None,
        "next_page_token": None,
    }
    expected_header_keys = ["Content-Type", "Api-Key", "Client-Request-Id", "Timestamp", "Auth-Token-Type", "Authorization"]
    assert list(stream.request_headers(**inputs).keys()) == expected_header_keys


def test_http_method(patch_base_class):
    stream = FiservStream(**config)
    expected_method = "POST"
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
    stream = FiservStream(**config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = FiservStream(**config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
