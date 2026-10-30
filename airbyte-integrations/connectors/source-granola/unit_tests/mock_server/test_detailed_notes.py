# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for incremental `detailed_notes` syncs through the parent state."""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import GranolaRequestBuilder


_NOW = "2026-01-15T12:00:00Z"
_START_DATE = "2025-10-12"
_STREAM_NAME = "detailed_notes"
_TRANSCRIPT_TOO_LARGE = {
    "code": "TRANSCRIPT_TOO_LARGE",
    "message": "Transcript is too large to return inline. Retrieve it in pages from /v1/notes/{note_id}/transcript.",
}


def _note(note_id: str, updated_at: str) -> Dict[str, Any]:
    return {
        "id": note_id,
        "title": f"Meeting {note_id}",
        "created_at": "2026-01-10T10:00:00Z",
        "updated_at": updated_at,
        "transcript": [],
    }


def _notes_request(updated_after: str) -> HttpRequest:
    return GranolaRequestBuilder.notes_endpoint().with_updated_after(updated_after).build()


def _notes_response(notes: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"notes": notes, "hasMore": False}), status_code=200)


def _detail_request(note_id: str) -> HttpRequest:
    return GranolaRequestBuilder.note_endpoint(note_id).with_include("transcript").build()


def _read(
    state: Optional[List[AirbyteStateMessage]] = None,
    sync_mode: SyncMode = SyncMode.incremental,
) -> EntrypointOutput:
    config = ConfigBuilder().with_start_date(_START_DATE).build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


def _stream_state(output: EntrypointOutput) -> Dict[str, Any]:
    return output.most_recent_state.stream_state.__dict__


@freezegun.freeze_time(_NOW)
class TestDetailedNotesIncremental(TestCase):
    @HttpMocker()
    def test_initial_sync_uses_start_date_and_tracks_parent_and_detail_state(self, http_mocker: HttpMocker):
        notes = [
            _note("note-1", "2026-01-10T09:00:00Z"),
            _note("note-2", "2026-01-12T08:00:00Z"),
        ]
        list_request = _notes_request("2025-10-12T00:00:00Z")
        http_mocker.get(list_request, _notes_response(notes))
        detail_requests = {note["id"]: _detail_request(note["id"]) for note in notes}
        for note in notes:
            http_mocker.get(detail_requests[note["id"]], HttpResponse(body=json.dumps(note), status_code=200))

        output = _read()

        assert output.errors == []
        assert len(output.records) == 2
        http_mocker.assert_number_of_calls(list_request, 1)
        for note in notes:
            http_mocker.assert_number_of_calls(detail_requests[note["id"]], 1)
        assert _stream_state(output) == {
            "use_global_cursor": True,
            "state": {"updated_at": "2026-01-12T08:00:00Z"},
            "lookback_window": 0,
            "parent_state": {"notes": {"updated_at": "2026-01-12T08:00:00Z"}},
        }

    @HttpMocker()
    def test_incremental_sync_reads_only_parent_notes_updated_since_saved_state(self, http_mocker: HttpMocker):
        list_request = _notes_request("2026-01-10T09:59:59Z")
        edited_note = _note("note-edited", "2026-01-12T08:00:00Z")
        http_mocker.get(list_request, _notes_response([edited_note]))
        detail_request = _detail_request("note-edited")
        http_mocker.get(detail_request, HttpResponse(body=json.dumps(edited_note), status_code=200))
        prior_state = {
            "use_global_cursor": True,
            "state": {"updated_at": "2026-01-10T10:00:00Z"},
            "lookback_window": 0,
            "parent_state": {"notes": {"updated_at": "2026-01-10T10:00:00Z"}},
        }

        output = _read(StateBuilder().with_stream_state(_STREAM_NAME, prior_state).build())

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["note-edited"]
        http_mocker.assert_number_of_calls(list_request, 1)
        http_mocker.assert_number_of_calls(detail_request, 1)
        assert _stream_state(output) == {
            "use_global_cursor": True,
            "state": {"updated_at": "2026-01-12T08:00:00Z"},
            "lookback_window": 0,
            "parent_state": {"notes": {"updated_at": "2026-01-12T08:00:00Z"}},
        }

    @HttpMocker()
    def test_fractional_updated_at_is_parsed_and_stored_at_second_precision(self, http_mocker: HttpMocker):
        list_request = _notes_request("2026-01-10T09:59:59Z")
        note = _note("note-fractional", "2026-01-12T08:00:00.462Z")
        http_mocker.get(list_request, _notes_response([note]))
        detail_request = _detail_request("note-fractional")
        http_mocker.get(detail_request, HttpResponse(body=json.dumps(note), status_code=200))
        prior_state = {
            "use_global_cursor": True,
            "state": {"updated_at": "2026-01-10T10:00:00Z"},
            "lookback_window": 0,
            "parent_state": {"notes": {"updated_at": "2026-01-10T10:00:00Z"}},
        }

        output = _read(StateBuilder().with_stream_state(_STREAM_NAME, prior_state).build())

        assert output.errors == []
        assert output.records[0].record.data["updated_at"] == "2026-01-12T08:00:00.462Z"
        assert _stream_state(output)["state"]["updated_at"] == "2026-01-12T08:00:00Z"

    @HttpMocker()
    def test_full_refresh_still_reads_parent_from_start_date(self, http_mocker: HttpMocker):
        note = _note("note-full-refresh", "2026-01-12T08:00:00Z")
        list_request = _notes_request("2025-10-12T00:00:00Z")
        http_mocker.get(list_request, _notes_response([note]))
        detail_request = _detail_request(note["id"])
        http_mocker.get(detail_request, HttpResponse(body=json.dumps(note), status_code=200))

        output = _read(sync_mode=SyncMode.full_refresh)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["note-full-refresh"]
        http_mocker.assert_number_of_calls(list_request, 1)
        http_mocker.assert_number_of_calls(detail_request, 1)

    @HttpMocker()
    def test_413_skips_note_and_emits_advanced_parent_state(self, http_mocker: HttpMocker):
        notes = [
            _note("note-small", "2026-01-11T08:00:00Z"),
            _note("note-large", "2026-01-12T08:00:00Z"),
        ]
        list_request = _notes_request("2026-01-10T09:59:59Z")
        http_mocker.get(list_request, _notes_response(notes))
        small_request = _detail_request("note-small")
        http_mocker.get(small_request, HttpResponse(body=json.dumps(notes[0]), status_code=200))
        oversized_request = _detail_request("note-large")
        http_mocker.get(oversized_request, HttpResponse(body=json.dumps(_TRANSCRIPT_TOO_LARGE), status_code=413))
        prior_state = {
            "use_global_cursor": True,
            "state": {"updated_at": "2026-01-10T10:00:00Z"},
            "lookback_window": 0,
            "parent_state": {"notes": {"updated_at": "2026-01-10T10:00:00Z"}},
        }

        output = _read(StateBuilder().with_stream_state(_STREAM_NAME, prior_state).build())

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["note-small"]
        http_mocker.assert_number_of_calls(list_request, 1)
        http_mocker.assert_number_of_calls(small_request, 1)
        http_mocker.assert_number_of_calls(oversized_request, 1)
        assert output.most_recent_state is not None
        state = _stream_state(output)
        assert state["use_global_cursor"] is True
        assert state["parent_state"]["notes"]["updated_at"] == "2026-01-12T08:00:00Z"
