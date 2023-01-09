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
    expected_params = {"tableName": "messages", "format": "convex_json"}
    assert stream.request_params(**inputs) == expected_params
    stream._snapshot_cursor_value = 1234
    expected_params = {"tableName": "messages", "format": "convex_json", "cursor": 1234}
    assert stream.request_params(**inputs) == expected_params
    stream._snapshot_has_more = False
    stream._delta_cursor_value = 2345
    expected_params = {"tableName": "messages", "format": "convex_json", "cursor": 2345}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 123}], "cursor": 1234, "snapshot": 5000, "hasMore": True}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) == {
        "snapshot_cursor": 1234,
        "snapshot_has_more": True,
        "delta_cursor": 5000,
    }
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1235}], "cursor": 1235, "snapshot": 5000, "hasMore": False}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) == {
        "snapshot_cursor": 1235,
        "snapshot_has_more": False,
        "delta_cursor": 5000,
    }
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1235}], "cursor": 6000, "hasMore": True}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) == {
        "snapshot_cursor": 1235,
        "snapshot_has_more": False,
        "delta_cursor": 6000,
    }
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1235}], "cursor": 7000, "hasMore": False}
    stream.parse_response(resp, {})
    assert stream.next_page_token(resp) is None
    assert stream.state == {"snapshot_cursor": 1235, "snapshot_has_more": False, "delta_cursor": 7000}


def test_parse_response(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1234}], "cursor": 1234, "snapshot": 2000, "hasMore": True}
    inputs = {"response": resp, "stream_state": {}}
    expected_parsed_objects = [{"_id": "my_id", "field": "f", "_ts": 1234}]
    assert stream.parse_response(**inputs) == expected_parsed_objects
    assert stream.state == {"snapshot_cursor": 1234, "snapshot_has_more": True, "delta_cursor": 2000}


def test_request_headers(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "messages", None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert stream.request_headers(**inputs) == {}


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
