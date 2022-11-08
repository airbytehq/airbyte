#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_outreach.source import OutreachStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OutreachStream, "path", "v0/example_endpoint")
    mocker.patch.object(OutreachStream, "primary_key", "id")
    mocker.patch.object(OutreachStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = OutreachStream(authenticator=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"count": "false", "page[size]": 100}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = OutreachStream(authenticator=MagicMock())
    response = MagicMock()
    response.json.return_value = {"links": {"next": "http://api.outreach.io/api/v2/prospects?page[after]=100"}}
    inputs = {"response": response}
    expected_token = {"after": "100"}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = OutreachStream(authenticator=MagicMock())
    response = MagicMock()
    response.json.return_value = {
        "data": [{"id": 123, "attributes": {"name": "John Doe"}, "relationships": {"account": {"data": {"type": "account", "id": 4}}}}]
    }
    inputs = {"response": response}
    expected_parsed_object = {"id": 123, "name": "John Doe"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = OutreachStream(authenticator=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = OutreachStream(authenticator=MagicMock())
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
    stream = OutreachStream(authenticator=MagicMock())
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = OutreachStream(authenticator=MagicMock())
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
