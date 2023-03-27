#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_fortnox.source import FortnoxStream, PAGE_SIZE


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(FortnoxStream, "path", "v0/example_endpoint")
    mocker.patch.object(FortnoxStream, "root_element", "test")
    mocker.patch.object(FortnoxStream, "primary_key", "test_primary_key")
    mocker.patch.object(FortnoxStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = FortnoxStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"limit": PAGE_SIZE}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = FortnoxStream()
    inputs = {
        "response": MagicMock(status_code=200, response={}, json=lambda: {"MetaInformation": {"@CurrentPage": 1, "@TotalPages": 2}})
    }
    expected_token = {"page": 2}
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_on_last_page(patch_base_class):
    stream = FortnoxStream()
    inputs = {
        "response": MagicMock(status_code=200, response={}, json=lambda: {"MetaInformation": {"@CurrentPage": 2, "@TotalPages": 2}})
    }
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_no_paging(patch_base_class):
    stream = FortnoxStream()
    inputs = {
        "response": MagicMock(status_code=200, response={}, json=lambda: {})
    }
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = FortnoxStream()
    inputs = {"response": MagicMock(json=lambda: {"test": [{"payload": 123}]})}
    expected_parsed_object = {"payload": 123}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = FortnoxStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = FortnoxStream()
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
    stream = FortnoxStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = FortnoxStream()
    expected_backoff_time = 5
    assert stream.backoff_time(response_mock) == expected_backoff_time
