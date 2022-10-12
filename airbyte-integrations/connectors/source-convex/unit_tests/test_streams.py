#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_convex.source import ConvexStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ConvexStream, "path", "v0/example_endpoint")
    mocker.patch.object(ConvexStream, "primary_key", "test_primary_key")
    mocker.patch.object(ConvexStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"tableName": "messages"}
    assert stream.request_params(**inputs) == expected_params
    inputs = {"stream_slice": None, "stream_state": {"_ts": 1234}, "next_page_token": None}
    expected_params = {"tableName": "messages", "cursor": 1234}
    assert stream.request_params(**inputs) == expected_params
    inputs = {"stream_slice": None, "stream_state": {"_ts": 1234}, "next_page_token": {"_ts": 2345}}
    expected_params = {"tableName": "messages", "cursor": 2345}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1234}], "cursor": ""}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) == {"_ts": 1234}
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1234}], "cursor": "custom_cursor"}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) == {"_ts": "custom_cursor"}
    resp.json = lambda: {"values": [], "cursor": ""}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) is None


def test_parse_response(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1234}], "cursor": ""}
    inputs = {"response": resp, "stream_state": {}}
    expected_parsed_objects = [{"_id": "my_id", "field": "f", "_ts": 1234}]
    assert stream.parse_response(**inputs) == expected_parsed_objects


def test_request_headers(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
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
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
