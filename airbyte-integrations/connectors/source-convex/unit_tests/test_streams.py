#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
import responses
from source_convex.source import ConvexStream

from airbyte_cdk.models import SyncMode


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(ConvexStream, "primary_key", "test_primary_key")
    mocker.patch.object(ConvexStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"tableName": "messages", "format": "json"}
    assert stream.request_params(**inputs) == expected_params
    stream._snapshot_cursor_value = 1234
    expected_params = {"tableName": "messages", "format": "json", "cursor": 1234}
    assert stream.request_params(**inputs) == expected_params
    stream._snapshot_has_more = False
    stream._delta_cursor_value = 2345
    expected_params = {"tableName": "messages", "format": "json", "cursor": 2345}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 123}], "cursor": 1234, "snapshot": 5000, "hasMore": True}
    resp.status_code = 200
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


@responses.activate
def test_read_records_full_refresh(patch_base_class):
    stream = ConvexStream("http://mocked_base_url:8080", "accesskey", "json", "messages", None)
    snapshot0_resp = {"values": [{"_id": "my_id", "field": "f", "_ts": 123}], "cursor": 1234, "snapshot": 5000, "hasMore": True}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json",
        json=snapshot0_resp,
    )
    snapshot1_resp = {"values": [{"_id": "an_id", "field": "b", "_ts": 100}], "cursor": 2345, "snapshot": 5000, "hasMore": True}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json&cursor=1234&snapshot=5000",
        json=snapshot1_resp,
    )
    snapshot2_resp = {"values": [{"_id": "a_id", "field": "x", "_ts": 300}], "cursor": 3456, "snapshot": 5000, "hasMore": False}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json&cursor=2345&snapshot=5000",
        json=snapshot2_resp,
    )
    records = list(stream.read_records(SyncMode.full_refresh))
    assert len(records) == 3
    assert [record["field"] for record in records] == ["f", "b", "x"]
    assert stream.state == {"delta_cursor": 5000, "snapshot_cursor": 3456, "snapshot_has_more": False}


@responses.activate
def test_read_records_incremental(patch_base_class):
    stream = ConvexStream("http://mocked_base_url:8080", "accesskey", "json", "messages", None)
    snapshot0_resp = {"values": [{"_id": "my_id", "field": "f", "_ts": 123}], "cursor": 1234, "snapshot": 5000, "hasMore": True}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json",
        json=snapshot0_resp,
    )
    snapshot1_resp = {"values": [{"_id": "an_id", "field": "b", "_ts": 100}], "cursor": 2345, "snapshot": 5000, "hasMore": False}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json&cursor=1234&snapshot=5000",
        json=snapshot1_resp,
    )
    delta0_resp = {"values": [{"_id": "a_id", "field": "x", "_ts": 300}], "cursor": 6000, "hasMore": True}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/document_deltas?tableName=messages&format=json&cursor=5000",
        json=delta0_resp,
    )
    delta1_resp = {"values": [{"_id": "a_id", "field": "x", "_ts": 400}], "cursor": 7000, "hasMore": False}
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/document_deltas?tableName=messages&format=json&cursor=6000",
        json=delta1_resp,
    )
    records = list(stream.read_records(SyncMode.incremental))
    assert len(records) == 4
    assert [record["field"] for record in records] == ["f", "b", "x", "x"]
    assert stream.state == {"delta_cursor": 7000, "snapshot_cursor": 2345, "snapshot_has_more": False}


def test_parse_response(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    resp = MagicMock()
    resp.json = lambda: {"values": [{"_id": "my_id", "field": "f", "_ts": 1234}], "cursor": 1234, "snapshot": 2000, "hasMore": True}
    resp.status_code = 200
    inputs = {"response": resp, "stream_state": {}}
    expected_parsed_objects = [{"_id": "my_id", "field": "f", "_ts": 1234}]
    assert stream.parse_response(**inputs) == expected_parsed_objects


def test_request_headers(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert stream.request_headers(**inputs) == {"Convex-Client": "airbyte-export-0.4.0"}


def test_http_method(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
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
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
