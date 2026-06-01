# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for selected `source-gong` manifest behavior.

Gong requires any integration that lists calls to drop calls where `isPrivate` is `true`.
The `calls` and `extensiveCalls` streams each declare a `RecordFilter` in `manifest.yaml`
that enforces this requirement. These tests mock the Gong API responses and assert the
filter actually drops the private records at sync time.
"""

import time
from unittest.mock import Mock

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}


def _public_call(call_id: str) -> dict:
    return {
        "id": call_id,
        "url": f"https://us-20768.app.gong.io/call?id={call_id}",
        "title": f"Public call {call_id}",
        "scheduled": "2024-01-02T10:00:00Z",
        "started": "2024-01-02T10:00:00Z",
        "duration": 120,
        "primaryUserId": "1",
        "direction": "Inbound",
        "system": "Gong",
        "scope": "Internal",
        "media": "Video",
        "language": "eng",
        "workspaceId": "ws-1",
        "isPrivate": False,
    }


def _private_call(call_id: str) -> dict:
    return {**_public_call(call_id), "title": f"Private call {call_id}", "isPrivate": True}


def _public_extensive_call(call_id: str) -> dict:
    return {
        "metaData": {
            "id": call_id,
            "url": f"https://us-20768.app.gong.io/call?id={call_id}",
            "title": f"Public extensive call {call_id}",
            "scheduled": "2024-01-02T10:00:00Z",
            "started": "2024-01-02T10:00:00Z",
            "duration": 120,
            "direction": "Inbound",
            "isPrivate": False,
        },
    }


def _private_extensive_call(call_id: str) -> dict:
    call = _public_extensive_call(call_id)
    call["metaData"]["title"] = f"Private extensive call {call_id}"
    call["metaData"]["isPrivate"] = True
    return call


def _sync(stream_name: str):
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog)


@pytest.mark.parametrize(
    "stream_name,method,url,success_response",
    [
        pytest.param(
            "calls",
            "get",
            "https://api.gong.io/v2/calls",
            {"calls": [_public_call("public-1")], "records": {"totalRecords": 1, "currentPageSize": 1}},
            id="calls_get",
        ),
        pytest.param(
            "extensiveCalls",
            "post",
            "https://api.gong.io/v2/calls/extensive",
            {"calls": [_public_extensive_call("public-1")], "records": {"totalRecords": 1, "currentPageSize": 1}},
            id="extensive_calls_post",
        ),
    ],
)
def test_stream_retries_429_with_retry_after(stream_name, method, url, success_response, monkeypatch):
    sleep_mock = Mock()
    monkeypatch.setattr(time, "sleep", sleep_mock)

    responses = [
        {
            "status_code": 429,
            "headers": {"Retry-After": "7"},
            "json": {"error": "Too many requests"},
        },
        {
            "status_code": 200,
            "json": success_response,
        },
    ]

    with requests_mock.Mocker() as request_mocker:
        getattr(request_mocker, method)(url, responses)
        output = _sync(stream_name)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert any(7 <= duration <= 10 for duration in sleep_durations), f"expected Retry-After backoff, got {sleep_durations!r}"
    assert output.records


def test_calls_stream_drops_private_calls():
    """`calls` stream filters out records where `isPrivate` is `true`."""
    response = {
        "calls": [
            _public_call("public-1"),
            _private_call("private-1"),
            _public_call("public-2"),
            _private_call("private-2"),
        ],
        "records": {"totalRecords": 4, "currentPageSize": 4, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.gong.io/v2/calls", json=response)
        output = _sync("calls")

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["public-1", "public-2"], f"expected only public calls to be emitted, got {emitted_ids}"
    emitted_is_private = [record.record.data.get("isPrivate") for record in output.records]
    assert all(
        value is False for value in emitted_is_private
    ), f"expected all emitted calls to have isPrivate=False, got {emitted_is_private}"


def test_extensive_calls_stream_drops_private_calls():
    """`extensiveCalls` stream filters out records where `metaData.isPrivate` is `true`."""
    response = {
        "calls": [
            _public_extensive_call("public-1"),
            _private_extensive_call("private-1"),
            _public_extensive_call("public-2"),
            _private_extensive_call("private-2"),
        ],
        "records": {"totalRecords": 4, "currentPageSize": 4, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.post("https://api.gong.io/v2/calls/extensive", json=response)
        output = _sync("extensiveCalls")

    emitted_ids = [record.record.data["metaData"]["id"] for record in output.records]
    assert emitted_ids == ["public-1", "public-2"], f"expected only public extensive calls to be emitted, got {emitted_ids}"
    emitted_is_private = [record.record.data["metaData"].get("isPrivate") for record in output.records]
    assert all(
        value is False for value in emitted_is_private
    ), f"expected all emitted extensive calls to have isPrivate=False, got {emitted_is_private}"


def test_calls_stream_emits_no_records_when_all_private():
    """When every call in the response has `isPrivate: true`, the stream emits nothing."""
    response = {
        "calls": [_private_call("private-1"), _private_call("private-2")],
        "records": {"totalRecords": 2, "currentPageSize": 2, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.gong.io/v2/calls", json=response)
        output = _sync("calls")

    assert (
        output.records == []
    ), f"expected zero emitted records when all source records are private, got {[r.record.data['id'] for r in output.records]}"
