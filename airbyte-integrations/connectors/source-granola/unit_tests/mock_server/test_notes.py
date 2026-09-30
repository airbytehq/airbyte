# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `notes` stream incremental cursor.

`GET /v1/notes` filters on `updated_after` only — there is no `updated_before` —
so `notes` syncs in a single unbounded slice keyed on `updated_at`. These tests
pin the `updated_after` values sent and assert that notes edited after a
previous sync are re-emitted.
"""

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
_STREAM_NAME = "notes"


def _notes_request(updated_after: str) -> HttpRequest:
    return GranolaRequestBuilder.notes_endpoint().with_updated_after(updated_after).build()


def _notes_response(notes: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"notes": notes, "hasMore": False}), status_code=200)


def _read_notes(state: Optional[List[AirbyteStateMessage]] = None) -> EntrypointOutput:
    config = ConfigBuilder().with_start_date(_START_DATE).build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


@freezegun.freeze_time(_NOW)
class TestNotesIncrementalUpdatedAtCursor(TestCase):
    @HttpMocker()
    def test_initial_sync_requests_single_slice_from_start_date(self, http_mocker: HttpMocker):
        """With no `updated_before` in the API, the whole range is one slice bounded by start_date."""
        notes = [
            {"id": "note-1", "created_at": "2025-10-20T10:00:00Z", "updated_at": "2025-11-02T09:00:00Z"},
            {"id": "note-2", "created_at": "2025-12-01T08:00:00Z", "updated_at": "2026-01-05T17:30:00Z"},
        ]
        request = _notes_request("2025-10-12T00:00:00Z")
        http_mocker.get(request, _notes_response(notes))

        output = _read_notes()

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        assert {message.record.data["id"] for message in output.records} == {"note-1", "note-2"}
        assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-01-05T17:30:00Z"

    @HttpMocker()
    def test_note_edited_after_first_sync_is_emitted_again_on_next_sync(self, http_mocker: HttpMocker):
        """A note created before the stored cursor but edited after it is replicated again."""
        request = _notes_request("2025-12-20T00:00:00Z")
        edited_note = {
            "id": "note-edited",
            "created_at": "2025-10-20T10:00:00Z",
            "updated_at": "2026-01-05T09:00:00Z",
        }
        http_mocker.get(request, _notes_response([edited_note]))

        output = _read_notes(StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2025-12-20T00:00:00Z"}).build())

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        assert {message.record.data["id"] for message in output.records} == {"note-edited"}

    @HttpMocker()
    def test_date_only_state_from_earlier_versions_resumes(self, http_mocker: HttpMocker):
        """Date-only cursor state still parses and resumes from midnight that day."""
        request = _notes_request("2025-12-20T00:00:00Z")
        http_mocker.get(request, _notes_response([]))

        output = _read_notes(StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": "2025-12-20"}).build())

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_legacy_created_at_state_restarts_from_start_date(self, http_mocker: HttpMocker):
        """State written by versions before 1.0.0 is keyed on `created_at`, so the
        `updated_at` cursor finds no value and restarts from start_date."""
        request = _notes_request("2025-10-12T00:00:00Z")
        http_mocker.get(request, _notes_response([]))

        output = _read_notes(StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": "2025-12-20T00:00:00Z"}).build())

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(_NOW)
class TestNotesPagination(TestCase):
    _UPDATED_AFTER = "2025-10-12T00:00:00Z"

    def _page(self, note_id: str, cursor: Optional[str], has_more: bool) -> HttpResponse:
        body = {
            "notes": [{"id": note_id, "created_at": "2026-01-12T09:00:00Z", "updated_at": "2026-01-12T09:00:00Z"}],
            "hasMore": has_more,
            "cursor": cursor,
        }
        return HttpResponse(body=json.dumps(body), status_code=200)

    @HttpMocker()
    def test_follows_the_cursor_while_has_more_is_true(self, http_mocker: HttpMocker):
        builder = GranolaRequestBuilder.notes_endpoint().with_updated_after(self._UPDATED_AFTER)
        first_page = builder.build()
        second_page = builder.with_cursor("cursor-2").build()
        http_mocker.get(first_page, self._page("note-page-1", cursor="cursor-2", has_more=True))
        http_mocker.get(second_page, self._page("note-page-2", cursor=None, has_more=False))

        output = _read_notes()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["note-page-1", "note-page-2"]
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_stops_when_has_more_is_false_even_if_a_cursor_is_returned(self, http_mocker: HttpMocker):
        request = _notes_request(self._UPDATED_AFTER)
        http_mocker.get(request, self._page("note-only", cursor="stale-cursor", has_more=False))

        output = _read_notes()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["note-only"]
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(_NOW)
class TestNotesDefaultStartDate(TestCase):
    @HttpMocker()
    def test_without_start_date_reads_the_last_730_days(self, http_mocker: HttpMocker):
        """The spec leaves `start_date` optional; the single slice then starts 730 days before now."""
        request = _notes_request("2024-01-16T00:00:00Z")
        http_mocker.get(request, _notes_response([]))

        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
