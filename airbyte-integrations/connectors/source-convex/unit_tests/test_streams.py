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
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


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
    ("http_status", "expected_action"),
    [
        (HTTPStatus.OK, ResponseAction.SUCCESS),
        (HTTPStatus.BAD_REQUEST, ResponseAction.FAIL),
        (HTTPStatus.TOO_MANY_REQUESTS, ResponseAction.RATE_LIMITED),
        (HTTPStatus.INTERNAL_SERVER_ERROR, ResponseAction.RETRY),
    ],
)
def test_error_handler_response_action(patch_base_class, http_status, expected_action):
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = http_status
    response_mock.ok = http_status < 400
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    assert stream._http_client._error_handler.interpret_response(response_mock).response_action == expected_action


def test_backoff_strategy(patch_base_class):
    stream = ConvexStream("murky-swan-635", "accesskey", "json", "messages", None)
    assert stream.get_backoff_strategy() is None


@responses.activate
def test_read_records_bad_request_fails_without_retry(patch_base_class):
    stream = ConvexStream("http://mocked_base_url:8080", "accesskey", "json", "messages", None)
    responses.add(
        responses.GET,
        "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json",
        json={"code": "BadRequest", "message": "bad request"},
        status=400,
    )
    with pytest.raises(Exception):
        list(stream.read_records(SyncMode.full_refresh))
    assert len(responses.calls) == 1


@pytest.mark.parametrize("http_status", [HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.INTERNAL_SERVER_ERROR])
@responses.activate
def test_read_records_retries_transient_errors(patch_base_class, mocker, http_status):
    mocker.patch("time.sleep")
    stream = ConvexStream("http://mocked_base_url:8080", "accesskey", "json", "messages", None)
    url = "http://mocked_base_url:8080/api/list_snapshot?tableName=messages&format=json"
    responses.add(responses.GET, url, json={"code": "Transient", "message": "try again"}, status=http_status)
    responses.add(
        responses.GET,
        url,
        json={"values": [{"_id": "my_id", "field": "f", "_ts": 123}], "cursor": 1234, "snapshot": 5000, "hasMore": False},
    )
    records = list(stream.read_records(SyncMode.full_refresh))
    assert [record["field"] for record in records] == ["f"]
    assert len(responses.calls) == 2
    assert stream.state == {"delta_cursor": 5000, "snapshot_cursor": 1234, "snapshot_has_more": False}
