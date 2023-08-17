#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import inspect
import json
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_xing.streams import XingStream
from source_xing.streams_customers import Customers

authenticator = ""
config = {}
parent = Customers


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(XingStream, "path", "v0/example_endpoint")
    mocker.patch.object(XingStream, "primary_key", "test_primary_key")
    mocker.patch.object(XingStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = XingStream(config, authenticator, parent)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = XingStream(config, authenticator, parent)
    inputs = {"response": MagicMock()}
    actual_result = stream.next_page_token(**inputs)
    assert actual_result is None or ("next_page" in actual_result and actual_result["next_page"] is not None), \
        f"Unexpected next_page_token result: {actual_result}"


def test_parse_response(patch_base_class):
    stream = XingStream(config, authenticator, parent)
    mock_response = {
        "customers": [],
        "totalCount": 5,
        "count": 0
    }
    mock_response = json.dumps(mock_response)
    response = requests.Response()
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'
    response._content = mock_response.encode('utf-8')
    result = stream.parse_response(response)
    expected_result = True
    assert inspect.isgenerator(result) == expected_result


def test_request_headers(patch_base_class):
    stream = XingStream(config, authenticator, parent)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = XingStream(config, authenticator, parent)
    expected_method = "GET"
    assert stream.http_method == expected_method


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = XingStream(config, authenticator, parent)
    expected_backoff_time = 60
    assert stream.backoff_time(response_mock) == expected_backoff_time


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
    stream = XingStream(config, authenticator, parent)
    assert stream.should_retry(response_mock) == should_retry
