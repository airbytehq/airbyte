#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock-server tests for sync tokens on Google Calendar metadata streams."""

import json
import logging
from typing import Any, Mapping, Optional

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "client_id": "id",
    "client_secret": "secret",
    "client_refresh_token_2": "rt",
    "calendarid": "primary",
}
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_TOKEN_REQUEST = HttpRequest(
    _TOKEN_URL,
    body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt",
)
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "at", "expires_in": 3600}))
_STREAM_URLS = {
    "settings": "https://www.googleapis.com/calendar/v3/users/me/settings",
    "calendarlist": "https://www.googleapis.com/calendar/v3/users/me/calendarList",
    "calendars": "https://www.googleapis.com/calendar/v3/users/me/calendarList",
}
_COMMITTED_AT = "2026-10-16T00:00:00Z"
_STREAM_NAMES = tuple(_STREAM_URLS)


def _request(stream_name: str, sync_token: Optional[str] = None, page_token: Optional[str] = None) -> HttpRequest:
    params = {}
    if sync_token is not None:
        params["syncToken"] = sync_token
    if page_token is not None:
        params["pageToken"] = page_token
    return HttpRequest(_STREAM_URLS[stream_name], query_params=params)


def _response(*records, next_page_token: Optional[str] = None, next_sync_token: Optional[str] = "tok1") -> HttpResponse:
    body: dict = {"items": list(records)}
    if next_page_token:
        body["nextPageToken"] = next_page_token
    elif next_sync_token is not None:
        body["nextSyncToken"] = next_sync_token
    return HttpResponse(json.dumps(body))


def _error_response(status_code: int, message: str, body_code: Any = None, reason: Optional[str] = None) -> HttpResponse:
    error: dict = {"message": message}
    if body_code is not None:
        error["code"] = body_code
    if reason:
        error["errors"] = [{"reason": reason, "domain": "global"}]
    return HttpResponse(json.dumps({"error": error}), status_code=status_code)


def _catalog(*stream_names: str):
    catalog = CatalogBuilder()
    for stream_name in stream_names:
        catalog.with_stream(stream_name, SyncMode.incremental)
    return catalog.build()


def _sync_token_state(stream_name: str, token: str):
    return (
        StateBuilder().with_stream_state(stream_name, {"state_type": "sync_token", "token": token, "committed_at": _COMMITTED_AT}).build()
    )


def _config(**overrides) -> Mapping[str, Any]:
    config = dict(_CONFIG)
    config.update(overrides)
    return config


def _read_stream(http_mocker: HttpMocker, stream_name: str, state=None, stream_names=None):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    config = _config()
    state = state or StateBuilder().build()
    source = get_source(config, state=state)
    return read(source, config, _catalog(*(stream_names or [stream_name])), state=state)


def _stream_state(message) -> Mapping[str, Any]:
    return json.loads(json.dumps(message.state.stream.stream_state, default=lambda obj: obj.__dict__))


def _emitted_states(output, stream_name: Optional[str] = None) -> list:
    states = []
    for message in output.state_messages:
        if message.state and message.state.stream:
            stream = message.state.stream
            if stream_name is None or stream.stream_descriptor.name == stream_name:
                states.append(_stream_state(message))
    return states


def _record_ids(output) -> list:
    return [message.record.data["id"] for message in output.records]


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_cold_multi_page_read_commits_token_after_last_page(stream_name):
    first_page = _request(stream_name)
    second_page = _request(stream_name, page_token="page-2")
    with HttpMocker() as http_mocker:
        http_mocker.get(first_page, _response({"id": "a"}, next_page_token="page-2"))
        http_mocker.get(second_page, _response({"id": "b"}, next_sync_token="tok1"))

        output = _read_stream(http_mocker, stream_name)

        assert output.errors == []
        assert _record_ids(output) == ["a", "b"]
        states = _emitted_states(output, stream_name)
        assert states[-1]["state_type"] == "sync_token"
        assert states[-1]["token"] == "tok1"
        assert "committed_at" in states[-1]
        assert all(state.get("token") != "tok1" for state in states[:-1])
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_warm_multi_page_read_sends_sync_token_on_each_page(stream_name):
    first_page = _request(stream_name, sync_token="tok0")
    second_page = _request(stream_name, sync_token="tok0", page_token="page-2")
    with HttpMocker() as http_mocker:
        http_mocker.get(first_page, _response({"id": "a"}, next_page_token="page-2"))
        http_mocker.get(second_page, _response({"id": "b"}, next_sync_token="tok2"))

        output = _read_stream(http_mocker, stream_name, state=_sync_token_state(stream_name, "tok0"))

        assert output.errors == []
        assert _record_ids(output) == ["a", "b"]
        assert _emitted_states(output, stream_name)[-1]["token"] == "tok2"
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_empty_terminal_page_commits_token(stream_name):
    request = _request(stream_name, sync_token="tok0")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _response(next_sync_token="tok1"))

        output = _read_stream(http_mocker, stream_name, state=_sync_token_state(stream_name, "tok0"))

        assert output.errors == []
        assert output.records == []
        assert _emitted_states(output, stream_name)[-1]["token"] == "tok1"
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_410_full_sync_required_resets_token_and_commits_replacement(stream_name):
    rejected_request = _request(stream_name, sync_token="tok0")
    restarted_request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(rejected_request, _error_response(410, "Sync token is no longer valid.", 410, "fullSyncRequired"))
        http_mocker.get(restarted_request, _response({"id": "a"}, next_sync_token="tok1"))

        output = _read_stream(http_mocker, stream_name, state=_sync_token_state(stream_name, "tok0"))

        assert output.errors == []
        assert _record_ids(output) == ["a"]
        assert _emitted_states(output, stream_name)[-1]["token"] == "tok1"
        http_mocker.assert_number_of_calls(rejected_request, 1)
        http_mocker.assert_number_of_calls(restarted_request, 1)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_400_invalid_sync_token_resets_token_and_commits_replacement(stream_name):
    rejected_request = _request(stream_name, sync_token="tok0")
    restarted_request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(rejected_request, _error_response(400, "Invalid sync token value.", 400))
        http_mocker.get(restarted_request, _response({"id": "a"}, next_sync_token="tok1"))

        output = _read_stream(http_mocker, stream_name, state=_sync_token_state(stream_name, "tok0"))

        assert output.errors == []
        assert _record_ids(output) == ["a"]
        assert _emitted_states(output, stream_name)[-1]["token"] == "tok1"
        http_mocker.assert_number_of_calls(rejected_request, 1)
        http_mocker.assert_number_of_calls(restarted_request, 1)


def test_calendarlist_emits_deleted_entries_on_warm_read():
    request = _request("calendarlist", sync_token="tok0")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _response({"id": "c1", "deleted": True}, next_sync_token="tok1"))

        output = _read_stream(http_mocker, "calendarlist", state=_sync_token_state("calendarlist", "tok0"))

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data["deleted"] is True
        http_mocker.assert_number_of_calls(request, 1)


def test_calendarlist_and_calendars_keep_independent_state():
    calendarlist_request = _request("calendarlist", sync_token="tok0")
    calendars_request = _request("calendars")
    state = _sync_token_state("calendarlist", "tok0")
    with HttpMocker() as http_mocker:
        http_mocker.get(calendarlist_request, _response({"id": "c1"}, next_sync_token="tok1"))
        http_mocker.get(calendars_request, _response({"id": "c2"}, next_sync_token="tok2"))

        output = _read_stream(
            http_mocker,
            "calendarlist",
            state=state,
            stream_names=["calendarlist", "calendars"],
        )

        assert output.errors == []
        assert set(_record_ids(output)) == {"c1", "c2"}
        http_mocker.assert_number_of_calls(calendarlist_request, 1)
        http_mocker.assert_number_of_calls(calendars_request, 1)


def test_discover_reports_incremental_support_without_cursor_fields():
    config = _config()
    catalog = get_source(config).discover(logging.getLogger("discover"), config)
    streams = {stream.name: stream for stream in catalog.streams}

    for stream_name in ("events", "settings", "calendarlist", "calendars"):
        assert SyncMode.incremental in streams[stream_name].supported_sync_modes
        assert streams[stream_name].source_defined_cursor is True

    assert streams["events"].default_cursor_field == ["updated"]
    for stream_name in ("settings", "calendarlist", "calendars"):
        assert streams[stream_name].default_cursor_field in (None, [])

    assert streams["colors"].supported_sync_modes == [SyncMode.full_refresh]
