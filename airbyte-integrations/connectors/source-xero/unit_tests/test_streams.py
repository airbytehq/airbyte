#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_xero.streams import XeroStream, parse_date


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


def test_parse_date():
    # 11/10/2020 00:00:00 +3 (11/10/2020 21:00:00 GMT/UTC)
    assert parse_date("/Date(1602363600000+0300)/") == datetime.datetime(2020, 10, 11, 0, 0, tzinfo=datetime.timezone.utc)
    # 02/02/2020 10:31:51.5 +3 (02/02/2020 07:31:51.5 GMT/UTC)
    assert parse_date("/Date(1580628711500+0300)/") == datetime.datetime(2020, 2, 2, 10, 31, 51, 500000, tzinfo=datetime.timezone.utc)
    # 07/02/2022 20:12:55 GMT/UTC
    assert parse_date("/Date(1656792775000)/") == datetime.datetime(2022, 7, 2, 20, 12, 55, tzinfo=datetime.timezone.utc)
    # Not a date
    assert parse_date("not a date") is None
