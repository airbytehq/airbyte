#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_xero.streams import XeroStream


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(XeroStream, "path", "v0/example_endpoint")
    mocker.patch.object(XeroStream, "primary_key", "test_primary_key")
    mocker.patch.object(XeroStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = XeroStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = XeroStream()
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token

    stream.page_size = 1
    stream.pagination = True
    response = MagicMock()
    response.json.return_value = {"XeroStream": [{}]}
    inputs = {"response": response}
    expected_token = {"has_next_page": True}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = XeroStream()
    response = MagicMock()
    response.json.return_value = {"XeroStream": [{"key": "value"}]}
    inputs = {"response": response}
    expected_parsed_object = {"key": "value"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = XeroStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Accept": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = XeroStream()
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
    stream = XeroStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = XeroStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
