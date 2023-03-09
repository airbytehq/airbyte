#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_tenkft.streams import TenkftStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(TenkftStream, "path", "v0/example_endpoint")
    mocker.patch.object(TenkftStream, "primary_key", "test_primary_key")
    mocker.patch.object(TenkftStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = TenkftStream("start_date", "end_date", "query")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"per_page": 1000}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = TenkftStream("start_date", "end_date", "query")
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = TenkftStream("start_date", "end_date", "query")
    mock_response = MagicMock()
    inputs = {"response": mock_response}
    expected_parsed_object = mock_response.json()
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = TenkftStream("start_date", "end_date", "query")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = TenkftStream("start_date", "end_date", "query")
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
    stream = TenkftStream("start_date", "end_date", "query")
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = TenkftStream("start_date", "end_date", "query")
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
