# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for Todoist Sync API incremental reads and independent stream tokens."""

import json
import logging
from typing import Any, Dict, List
from urllib.parse import urlencode

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://api.todoist.com/api/v1"
_TOKEN = "test-token"
_CONFIG = {"token": _TOKEN}
_COMMITTED_AT = "2026-10-01T00:00:00Z"


def _request(stream_name: str, sync_token: str) -> HttpRequest:
    resource_types = '["items"]' if stream_name == "tasks" else '["projects"]'
    body = urlencode({"resource_types": resource_types, "sync_token": sync_token})
    return HttpRequest(
        url=f"{_BASE_URL}/sync",
        body=body,
        headers={
            "Authorization": f"Bearer {_TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )


def _response(stream_name: str, records: List[Dict[str, Any]], sync_token: str) -> HttpResponse:
    records_key = "items" if stream_name == "tasks" else "projects"
    return HttpResponse(body=json.dumps({records_key: records, "sync_token": sync_token}), status_code=200)


def _cursor_state(stream_name: str, token: str):
    return (
        StateBuilder()
        .with_stream_state(
            stream_name,
            {"state_type": "opaque_token", "token": token, "committed_at": _COMMITTED_AT},
        )
        .build()
    )


def _read(stream_names: List[str], state=None) -> EntrypointOutput:
    state = state or StateBuilder().build()
    catalog_builder = CatalogBuilder()
    for stream_name in stream_names:
        catalog_builder = catalog_builder.with_stream(stream_name, SyncMode.incremental)
    catalog = catalog_builder.build()
    return read(get_source(config=_CONFIG, state=state), config=_CONFIG, catalog=catalog, state=state)


def _stream_state(output: EntrypointOutput, stream_name: str) -> Dict[str, Any]:
    for message in output.state_messages:
        if message.state and message.state.stream:
            stream_state = message.state.stream
            if stream_state.stream_descriptor.name == stream_name:
                return stream_state.stream_state.__dict__
    raise AssertionError(f"No emitted state for {stream_name}")


def _assert_committed_state(output: EntrypointOutput, stream_name: str, token: str) -> None:
    state = _stream_state(output, stream_name)
    assert state["state_type"] == "opaque_token"
    assert state["token"] == token
    assert set(state) == {"state_type", "token", "committed_at"}


@pytest.mark.parametrize(
    ("stream_name", "records"),
    [
        ("tasks", [{"id": "task-1", "updated_at": "2026-10-01T00:00:00Z"}]),
        ("projects", [{"id": "project-1", "updated_at": "2026-10-01T00:00:00Z"}]),
    ],
)
def test_cold_read_uses_wildcard_and_commits_terminal_token(stream_name: str, records: List[Dict[str, Any]]):
    request = _request(stream_name, "*")
    with HttpMocker() as http_mocker:
        http_mocker.post(request, _response(stream_name, records, "tok1"))

        output = _read([stream_name])

        assert output.errors == []
        assert [message.record.data for message in output.records] == records
        _assert_committed_state(output, stream_name, "tok1")
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", ["tasks", "projects"])
def test_warm_read_replays_stored_token_and_commits_new_token(stream_name: str):
    request = _request(stream_name, "tok0")
    state = _cursor_state(stream_name, "tok0")
    record = {"id": f"{stream_name}-1", "updated_at": "2026-10-02T00:00:00Z"}
    with HttpMocker() as http_mocker:
        http_mocker.post(request, _response(stream_name, [record], "tok2"))

        output = _read([stream_name], state)

    assert output.errors == []
    assert [message.record.data for message in output.records] == [record]
    _assert_committed_state(output, stream_name, "tok2")
    http_mocker.assert_number_of_calls(request, 1)


def test_empty_incremental_response_commits_new_token():
    request = _request("tasks", "tok0")
    with HttpMocker() as http_mocker:
        http_mocker.post(request, _response("tasks", [], "tok3"))

        output = _read(["tasks"], _cursor_state("tasks", "tok0"))

    assert output.errors == []
    assert output.records == []
    _assert_committed_state(output, "tasks", "tok3")
    http_mocker.assert_number_of_calls(request, 1)


def test_incremental_response_emits_checked_and_deleted_items():
    request = _request("tasks", "tok0")
    records = [
        {"id": "checked", "checked": True, "is_deleted": False, "updated_at": "2026-10-02T00:00:00Z"},
        {"id": "deleted", "checked": False, "is_deleted": True, "updated_at": "2026-10-02T00:01:00Z"},
    ]
    with HttpMocker() as http_mocker:
        http_mocker.post(request, _response("tasks", records, "tok2"))

        output = _read(["tasks"], _cursor_state("tasks", "tok0"))

    assert output.errors == []
    assert [message.record.data for message in output.records] == records
    _assert_committed_state(output, "tasks", "tok2")
    http_mocker.assert_number_of_calls(request, 1)


def test_tasks_and_projects_keep_requests_and_committed_tokens_independent():
    tasks_request = _request("tasks", "tasks-old")
    projects_request = _request("projects", "projects-old")
    tasks_state = {"state_type": "opaque_token", "token": "tasks-old", "committed_at": _COMMITTED_AT}
    projects_state = {"state_type": "opaque_token", "token": "projects-old", "committed_at": _COMMITTED_AT}
    state = StateBuilder().with_stream_state("tasks", tasks_state).with_stream_state("projects", projects_state).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(tasks_request, _response("tasks", [{"id": "task-1", "updated_at": "2026-10-02T00:00:00Z"}], "tasks-new"))
        http_mocker.post(
            projects_request, _response("projects", [{"id": "project-1", "updated_at": "2026-10-02T00:00:00Z"}], "projects-new")
        )

        output = _read(["tasks", "projects"], state)

    assert output.errors == []
    _assert_committed_state(output, "tasks", "tasks-new")
    _assert_committed_state(output, "projects", "projects-new")
    assert _stream_state(output, "tasks")["token"] != "projects-new"
    assert _stream_state(output, "projects")["token"] != "tasks-new"
    http_mocker.assert_number_of_calls(tasks_request, 1)
    http_mocker.assert_number_of_calls(projects_request, 1)


@pytest.mark.parametrize("legacy_state", [None, {"updated_at": "2025-08-10T12:00:00.000000Z"}])
def test_empty_or_legacy_state_starts_with_wildcard(legacy_state):
    request = _request("tasks", "*")
    state = StateBuilder().build() if legacy_state is None else StateBuilder().with_stream_state("tasks", legacy_state).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(request, _response("tasks", [], "tok1"))

        output = _read(["tasks"], state)

        assert output.errors == []
        assert output.records == []
        _assert_committed_state(output, "tasks", "tok1")
        http_mocker.assert_number_of_calls(request, 1)


def test_discovery_declares_both_streams_incremental_with_existing_schemas():
    catalog = get_source(config=_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG)
    streams = {stream.name: stream for stream in catalog.streams}
    assert set(streams) == {"tasks", "projects"}
    for stream in streams.values():
        assert SyncMode.incremental in stream.supported_sync_modes
        assert stream.source_defined_cursor is True
        assert stream.default_cursor_field == ["updated_at"]
        assert "id" in stream.json_schema["properties"]
