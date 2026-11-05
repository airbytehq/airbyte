# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {"client_id": "test-client", "client_secret": "test-secret", "user": 123}
STREAMS = ["events", "admin_logs"]


def request(stream, position=None):
    params = {"limit": "100"}
    if stream == "admin_logs":
        params["stream_type"] = "admin_logs"
    if position is not None:
        params["stream_position"] = position
    return HttpRequest("https://api.box.com/2.0/events", query_params=params)


def page(ids, token):
    return HttpResponse(
        json.dumps(
            {
                "entries": [{"event_id": event_id, "type": "event"} for event_id in ids],
                "chunk_size": len(ids),
                "next_stream_position": token,
            }
        )
    )


def authenticate(mocker):
    mocker.post(
        HttpRequest(
            "https://api.box.com/oauth2/token",
            body="grant_type=client_credentials&client_id=test-client&client_secret=test-secret&box_subject_id=123&box_subject_type=user",
        ),
        HttpResponse(json.dumps({"access_token": "test-token", "expires_in": 3600})),
    )


def state_for(tokens):
    builder = StateBuilder()
    for stream, token in tokens.items():
        builder.with_stream_state(stream, {"state_type": "sync_token", "token": token})
    return builder.build()


def run_read(streams, tokens=None, mode=SyncMode.incremental):
    state = state_for(tokens or {})
    catalog = CatalogBuilder()
    for stream in streams:
        catalog.with_stream(stream, mode)
    return read(get_source(CONFIG, state), config=CONFIG, catalog=catalog.build(), state=state)


def assert_tokens(output, expected):
    assert output.errors == []
    actual = {}
    for message in output.state_messages:
        stream = message.state.stream
        state = stream.stream_state.__dict__
        assert state.get("committed_at")
        actual[stream.stream_descriptor.name] = {key: value for key, value in state.items() if key != "committed_at"}
    assert actual == {stream: {"state_type": "sync_token", "token": token} for stream, token in expected.items()}


def test_discover():
    catalog = get_source(CONFIG).discover(logging.getLogger(), CONFIG)
    for stream in catalog.streams:
        if stream.name in STREAMS:
            assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
            assert stream.source_defined_cursor is True
            assert not stream.default_cursor_field
        else:
            assert stream.supported_sync_modes == [SyncMode.full_refresh]


@pytest.mark.parametrize("stream", STREAMS)
@pytest.mark.parametrize("warm", [False, True])
def test_paginated_read(stream, warm):
    with HttpMocker() as mocker:
        authenticate(mocker)
        first = request(stream, "stored" if warm else None)
        second = request(stream, "page-2")
        terminal = request(stream, "page-3")
        mocker.get(first, page(["change"], "page-2"))
        mocker.get(second, page(["another-change"], "page-3"))
        mocker.get(terminal, page([], "committed"))
        output = run_read([stream], {stream: "stored"} if warm else {})
        assert_tokens(output, {stream: "committed"})
        assert [m.record.data["event_id"] for m in output.records] == ["change", "another-change"]
        for req in [first, second, terminal]:
            mocker.assert_number_of_calls(req, 1)


@pytest.mark.parametrize("stream", STREAMS)
def test_empty_warm_read(stream):
    with HttpMocker() as mocker:
        authenticate(mocker)
        mocker.get(request(stream, "stored"), page([], "advanced"))
        output = run_read([stream], {stream: "stored"})
        assert_tokens(output, {stream: "advanced"})
        assert output.records == []


@pytest.mark.parametrize("stream", STREAMS)
def test_invalid_token_resets(stream):
    with HttpMocker() as mocker:
        authenticate(mocker)
        expired = request(stream, "expired")
        cold = request(stream)
        mocker.get(
            expired,
            HttpResponse(
                json.dumps(
                    {
                        "type": "error",
                        "status": 400,
                        "code": "bad_request",
                        "message": "Invalid stream_position",
                    }
                ),
                status_code=400,
            ),
        )
        mocker.get(cold, page(["recovered"], "page-2"))
        mocker.get(request(stream, "page-2"), page([], "new-token"))
        output = run_read([stream], {stream: "expired"})
        assert_tokens(output, {stream: "new-token"})
        assert [m.record.data["event_id"] for m in output.records] == ["recovered"]
        mocker.assert_number_of_calls(expired, 1)
        mocker.assert_number_of_calls(cold, 1)


def test_state_isolation():
    with HttpMocker() as mocker:
        authenticate(mocker)
        for stream in STREAMS:
            mocker.get(request(stream, stream + "-old"), page([], stream + "-new"))
        output = run_read(STREAMS, {stream: stream + "-old" for stream in STREAMS})
        assert_tokens(output, {stream: stream + "-new" for stream in STREAMS})


@pytest.mark.parametrize("stream", STREAMS)
def test_full_refresh(stream):
    with HttpMocker() as mocker:
        authenticate(mocker)
        mocker.get(request(stream), page(["first"], "page-2"))
        mocker.get(request(stream, "page-2"), page(["second"], "page-3"))
        mocker.get(request(stream, "page-3"), page([], "terminal"))
        output = run_read([stream], mode=SyncMode.full_refresh)
        assert output.errors == []
        assert [m.record.data["event_id"] for m in output.records] == ["first", "second"]
