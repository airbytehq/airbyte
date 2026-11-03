# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest import TestCase

from config_builder import ConfigBuilder
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, TState, YamlDeclarativeSource
from airbyte_cdk.models import FailureType
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
_STREAM_NAME = "chats"
_SUBDOMAIN = "a_subdomain"
_BASE_URL = f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat"
_SEARCH_URL = f"{_BASE_URL}/chats/search"
_CHATS_URL = f"{_BASE_URL}/chats"

# The parent search runs in one-day windows between the cursor (or `start_date`) and "now". Freezing "now" keeps
# the set of windows, and therefore the set of requests to mock, deterministic.
_NOW = "2021-01-03T12:00:00Z"
_START_DATETIME = datetime(2021, 1, 1, tzinfo=timezone.utc)
_WINDOWS = [
    ("2021-01-01T00:00:00Z", "2021-01-01T23:59:59Z"),
    ("2021-01-02T00:00:00Z", "2021-01-02T23:59:59Z"),
    ("2021-01-03T00:00:00Z", _NOW),
]

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def _catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _chat_id(number: int) -> str:
    return f"2101.10414779.chat{number:04d}"


def _search_result(chat_id: str, timestamp: str) -> Dict[str, Any]:
    return {"id": chat_id, "timestamp": timestamp, "preview": "Hi there!", "type": "offline_msg", "url": f"{_CHATS_URL}/{chat_id}"}


def _chat(chat_id: str, timestamp: str) -> Dict[str, Any]:
    return {
        "id": chat_id,
        "type": "offline_msg",
        "timestamp": timestamp,
        "unread": False,
        "message": "Hi there!",
        "department_id": None,
        "department_name": None,
        "visitor": {"id": "3.45678", "name": "Jiny", "email": "visitor@example.com"},
        "session": {"id": "141109.654464.1KhqS0Nw"},
        "webpath": [],
        "zendesk_ticket_id": None,
    }


def _search_request(start: str, end: str, page: Optional[int] = None) -> HttpRequest:
    query_params = {"q": f"update_timestamp:[{start} TO {end}]"}
    if page:
        query_params["page"] = str(page)
    return HttpRequest(_SEARCH_URL, query_params=query_params)


def _search_response(results: List[Dict[str, Any]], count: Optional[int] = None, next_page: Optional[int] = None) -> HttpResponse:
    next_url = f"{_SEARCH_URL}?q=update_timestamp&page={next_page}" if next_page else None
    body = {"results": results, "count": count if count is not None else len(results), "prev_url": None, "next_url": next_url}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _chats_request(chat_ids: List[str]) -> HttpRequest:
    return HttpRequest(_CHATS_URL, query_params={"ids": ",".join(chat_ids)})


def _chats_response(chats: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"docs": {chat["id"]: chat for chat in chats}, "count": len(chats)}), status_code=200)


def _mock_empty_windows(http_mocker: HttpMocker, windows: List[tuple]) -> None:
    for start, end in windows:
        http_mocker.get(_search_request(start, end), _search_response([]))


def read(
    config_builder: Optional[ConfigBuilder] = None,
    state_builder: Optional[StateBuilder] = None,
    expecting_exception: bool = False,
    sync_mode: SyncMode = SyncMode.full_refresh,
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state, expecting_exception)


def _config() -> ConfigBuilder:
    return ConfigBuilder().start_date(_START_DATETIME).subdomain(_SUBDOMAIN)


@freeze_time(_NOW)
class ChatsTest(TestCase):
    @HttpMocker()
    def test_404_on_search_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_search_request(*_WINDOWS[0]), HttpResponse(body='{"error": "Not Found"}', status_code=404))
        _mock_empty_windows(http_mocker, _WINDOWS[1:])

        output = read(_config())

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_when_read_then_chats_found_by_search_are_fetched_by_id(self, http_mocker: HttpMocker) -> None:
        """Chats are located with one search per day window and then fetched in full with `chats?ids=`."""
        chats = [_chat(_chat_id(1), "2021-01-01T10:00:00Z"), _chat(_chat_id(2), "2021-01-01T11:00:00Z")]
        http_mocker.get(_search_request(*_WINDOWS[0]), _search_response([_search_result(c["id"], c["timestamp"]) for c in chats]))
        _mock_empty_windows(http_mocker, _WINDOWS[1:])
        http_mocker.get(_chats_request([c["id"] for c in chats]), _chats_response(chats))

        output = read(_config())

        assert sorted(r.record.data["id"] for r in output.records) == [c["id"] for c in chats]
        # Records are the full chats from `chats?ids=`, not the search summaries.
        assert all("message" in r.record.data and "preview" not in r.record.data for r in output.records)

    @HttpMocker()
    def test_given_search_spans_pages_when_read_then_paginate_and_fetch_in_groups_of_50(self, http_mocker: HttpMocker) -> None:
        """A window with 51 results takes two search pages (40 per page) and two `chats?ids=` requests (50 ids max)."""
        chats = [_chat(_chat_id(i), f"2021-01-01T{i // 60:02d}:{i % 60:02d}:00Z") for i in range(1, 52)]
        results = [_search_result(c["id"], c["timestamp"]) for c in chats]
        http_mocker.get(_search_request(*_WINDOWS[0]), _search_response(results[:40], count=51, next_page=2))
        http_mocker.get(_search_request(*_WINDOWS[0], page=2), _search_response(results[40:], count=51))
        _mock_empty_windows(http_mocker, _WINDOWS[1:])
        http_mocker.get(_chats_request([c["id"] for c in chats[:50]]), _chats_response(chats[:50]))
        http_mocker.get(_chats_request([c["id"] for c in chats[50:]]), _chats_response(chats[50:]))

        output = read(_config())

        assert len(output.records) == 51
        assert len({r.record.data["id"] for r in output.records}) == 51

    @HttpMocker()
    def test_given_10000_results_when_read_then_window_is_split(self, http_mocker: HttpMocker) -> None:
        """
        Zendesk serves at most 10,000 results per search (250 pages of 40). A first page whose `count` reaches that cap is
        not read; the day is split in halves and each half is searched on its own, so nothing is lost or emitted twice.
        """
        overflow_page = _search_response([_search_result(_chat_id(99), "2021-01-01T00:00:01Z")], count=10000, next_page=2)
        first_half = ("2021-01-01T00:00:00Z", "2021-01-01T11:59:59Z")
        second_half = ("2021-01-01T12:00:00Z", "2021-01-01T23:59:59Z")
        chats = [_chat(_chat_id(1), "2021-01-01T10:00:00Z"), _chat(_chat_id(2), "2021-01-01T15:00:00Z")]
        http_mocker.get(_search_request(*_WINDOWS[0]), overflow_page)
        http_mocker.get(_search_request(*first_half), _search_response([_search_result(chats[0]["id"], chats[0]["timestamp"])]))
        http_mocker.get(_search_request(*second_half), _search_response([_search_result(chats[1]["id"], chats[1]["timestamp"])]))
        _mock_empty_windows(http_mocker, _WINDOWS[1:])
        http_mocker.get(_chats_request([c["id"] for c in chats]), _chats_response(chats))

        output = read(_config())

        assert sorted(r.record.data["id"] for r in output.records) == [c["id"] for c in chats]
        assert not output.errors

    @HttpMocker()
    def test_given_every_window_at_cap_when_read_then_fail_after_ten_splits(self, http_mocker: HttpMocker) -> None:
        """The CDK splits a window at most ten times (a day shrinks to about 84 seconds), then the sync fails explicitly."""
        at_cap = _search_response([_search_result(_chat_id(99), "2021-01-01T00:00:01Z")], count=10000, next_page=2)
        any_search = HttpRequest(_SEARCH_URL, query_params=ANY_QUERY_PARAMS)
        http_mocker.get(any_search, at_cap)

        output = read(_config(), expecting_exception=True)

        # The first window plus one first-half window per split level, before the sync stops.
        http_mocker.assert_number_of_calls(any_search, 11)
        assert len(output.records) == 0
        assert any(
            error.trace.error.failure_type == FailureType.transient_error
            and "the chats stream cannot completely read a window" in error.trace.error.message
            for error in output.errors
        )

    @HttpMocker()
    def test_given_chat_found_in_two_windows_when_read_then_fetched_once(self, http_mocker: HttpMocker) -> None:
        """The same id can come back from two search windows (lookback, split); the group deduplicates it."""
        chat = _chat(_chat_id(1), "2021-01-01T23:59:59Z")
        result = _search_result(chat["id"], chat["timestamp"])
        http_mocker.get(_search_request(*_WINDOWS[0]), _search_response([result]))
        http_mocker.get(_search_request(*_WINDOWS[1]), _search_response([result]))
        _mock_empty_windows(http_mocker, _WINDOWS[2:])
        fetch = _chats_request([chat["id"]])
        http_mocker.get(fetch, _chats_response([chat]))

        output = read(_config())

        http_mocker.assert_number_of_calls(fetch, 1)
        assert [r.record.data["id"] for r in output.records] == [chat["id"]]

    @HttpMocker()
    def test_given_missing_chat_in_fetch_when_read_then_null_doc_is_skipped(self, http_mocker: HttpMocker) -> None:
        """List Chats answers an id it no longer has (deleted between the search and the fetch) with `"<id>": null`."""
        present = _chat(_chat_id(1), "2021-01-01T10:00:00Z")
        missing_id = _chat_id(2)
        results = [_search_result(present["id"], present["timestamp"]), _search_result(missing_id, "2021-01-01T11:00:00Z")]
        http_mocker.get(_search_request(*_WINDOWS[0]), _search_response(results))
        _mock_empty_windows(http_mocker, _WINDOWS[1:])
        http_mocker.get(
            _chats_request([present["id"], missing_id]),
            HttpResponse(body=json.dumps({"docs": {present["id"]: present, missing_id: None}, "count": 1}), status_code=200),
        )

        output = read(_config())

        assert [r.record.data["id"] for r in output.records] == [present["id"]]
        assert not output.errors

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker) -> None:
        """The stream cursor is `timestamp`; the state also carries the parent search cursor."""
        chats = [_chat(_chat_id(1), "2021-01-01T10:00:00Z"), _chat(_chat_id(2), "2021-01-02T08:00:00Z")]
        http_mocker.get(_search_request(*_WINDOWS[0]), _search_response([_search_result(chats[0]["id"], chats[0]["timestamp"])]))
        http_mocker.get(_search_request(*_WINDOWS[1]), _search_response([_search_result(chats[1]["id"], chats[1]["timestamp"])]))
        _mock_empty_windows(http_mocker, _WINDOWS[2:])
        # Ids found in different windows are fetched together: groups of 50 ids span search windows.
        http_mocker.get(_chats_request([chats[0]["id"], chats[1]["id"]]), _chats_response(chats))

        output = read(_config(), sync_mode=SyncMode.incremental)

        assert len(output.records) == 2
        latest_state = output.most_recent_state.stream_state.__dict__
        assert latest_state["state"] == {"timestamp": "2021-01-02T08:00:00Z"}
        assert latest_state["parent_state"] == {"chats_search": {"timestamp": "2021-01-02T08:00:00Z"}}

    def _assert_legacy_state_is_migrated(self, http_mocker: HttpMocker, legacy_cursor_value: Any) -> None:
        """
        A state written before 2.0.0 (`{"update_timestamp": <epoch seconds or ISO>}`) seeds both cursors. With a cursor of
        2021-01-02T00:00:00Z the search restarts one day earlier (lookback), so the first window is 2021-01-01, and a chat
        started before the cursor but updated inside the window is emitted again.
        """
        old_chat = _chat(_chat_id(1), "2020-12-15T10:00:00Z")
        http_mocker.get(_search_request(*_WINDOWS[0]), _search_response([]))
        http_mocker.get(_search_request(*_WINDOWS[1]), _search_response([_search_result(old_chat["id"], old_chat["timestamp"])]))
        _mock_empty_windows(http_mocker, _WINDOWS[2:])
        http_mocker.get(_chats_request([old_chat["id"]]), _chats_response([old_chat]))

        output = read(
            ConfigBuilder().start_date(datetime(2020, 10, 1, tzinfo=timezone.utc)).subdomain(_SUBDOMAIN),
            StateBuilder().with_stream_state(_STREAM_NAME, {"update_timestamp": legacy_cursor_value}),
            sync_mode=SyncMode.incremental,
        )

        assert [r.record.data["id"] for r in output.records] == [old_chat["id"]]
        latest_state = output.most_recent_state.stream_state.__dict__
        assert latest_state["state"] == {"timestamp": "2021-01-02T00:00:00Z"}
        assert latest_state["parent_state"] == {"chats_search": {"timestamp": "2021-01-02T00:00:00Z"}}

    @HttpMocker()
    def test_given_legacy_epoch_state_when_read_then_state_is_migrated(self, http_mocker: HttpMocker) -> None:
        self._assert_legacy_state_is_migrated(http_mocker, "1609545600")

    @HttpMocker()
    def test_given_legacy_iso_state_when_read_then_state_is_migrated(self, http_mocker: HttpMocker) -> None:
        self._assert_legacy_state_is_migrated(http_mocker, "2021-01-02T00:00:00Z")

    @HttpMocker()
    def test_given_new_state_when_read_then_resume_from_parent_state(self, http_mocker: HttpMocker) -> None:
        state = {
            "use_global_cursor": True,
            "state": {"timestamp": "2021-01-02T00:00:00Z"},
            "parent_state": {"chats_search": {"timestamp": "2021-01-02T00:00:00Z"}},
        }
        _mock_empty_windows(http_mocker, _WINDOWS)

        output = read(
            ConfigBuilder().start_date(datetime(2020, 10, 1, tzinfo=timezone.utc)).subdomain(_SUBDOMAIN),
            StateBuilder().with_stream_state(_STREAM_NAME, state),
            sync_mode=SyncMode.incremental,
        )

        assert len(output.records) == 0
        assert output.most_recent_state.stream_state.__dict__["state"] == {"timestamp": "2021-01-02T00:00:00Z"}
