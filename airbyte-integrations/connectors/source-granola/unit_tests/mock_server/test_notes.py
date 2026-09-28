# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `notes` stream incremental slice bounds.

`GET /v1/notes` treats `created_before=<date>` as excluding that whole day, so
day-truncated slice bounds dropped every note created on a slice boundary day.
These tests pin the exact `created_after` / `created_before` pairs sent across
several 30-day slices and assert that boundary-day notes are emitted.
"""

import json
from datetime import datetime, timedelta, timezone
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

# With start_date 2025-10-12, step P30D and second-granular bounds, adjacent
# slices are contiguous: each ends at 23:59:59Z of the day the next one starts.
_SLICE_BOUNDS = [
    ("2025-10-12T00:00:00Z", "2025-11-10T23:59:59Z"),
    ("2025-11-11T00:00:00Z", "2025-12-10T23:59:59Z"),
    ("2025-12-11T00:00:00Z", "2026-01-09T23:59:59Z"),
    ("2026-01-10T00:00:00Z", _NOW),
]

# Notes created on a slice boundary day - the records the day-truncated bounds dropped.
_BOUNDARY_NOTES = [
    {"id": "note-boundary-1", "created_at": "2025-11-10T15:00:00Z"},
    {"id": "note-boundary-2", "created_at": "2025-12-10T08:30:00Z"},
    {"id": "note-boundary-3", "created_at": "2026-01-09T23:59:59Z"},
]
_MID_SLICE_NOTE = {"id": "note-mid-slice", "created_at": "2025-10-20T10:00:00Z"}


def _notes_request(created_after: str, created_before: str) -> HttpRequest:
    return GranolaRequestBuilder.notes_endpoint().with_created_after(created_after).with_created_before(created_before).build()


def _notes_response(notes: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"notes": notes, "hasMore": False}), status_code=200)


def _notes_within(created_after: str, created_before: str) -> List[Dict[str, Any]]:
    """The notes a correct API would return for the given slice bounds."""
    return [note for note in _BOUNDARY_NOTES + [_MID_SLICE_NOTE] if created_after <= note["created_at"] <= created_before]


def _read_notes(state: Optional[List[AirbyteStateMessage]] = None) -> EntrypointOutput:
    config = ConfigBuilder().with_start_date(_START_DATE).build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


@freezegun.freeze_time(_NOW)
class TestNotesIncrementalSliceBounds(TestCase):
    @HttpMocker()
    def test_slice_bounds_are_contiguous_second_granular_datetimes(self, http_mocker: HttpMocker):
        """Every slice is requested with second-granular bounds, leaving no gap between slices."""
        requests = [_notes_request(created_after, created_before) for created_after, created_before in _SLICE_BOUNDS]
        for request in requests:
            http_mocker.get(request, _notes_response([]))

        output = _read_notes()

        assert output.errors == []
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_notes_created_on_a_slice_boundary_day_are_emitted(self, http_mocker: HttpMocker):
        for created_after, created_before in _SLICE_BOUNDS:
            http_mocker.get(
                _notes_request(created_after, created_before),
                _notes_response(_notes_within(created_after, created_before)),
            )

        output = _read_notes()

        emitted_ids = {message.record.data["id"] for message in output.records}
        assert emitted_ids == {note["id"] for note in _BOUNDARY_NOTES} | {_MID_SLICE_NOTE["id"]}

    @HttpMocker()
    def test_date_only_state_from_earlier_versions_resumes(self, http_mocker: HttpMocker):
        """Versions up to 0.2.13 persisted date-only cursors, which must still resume."""
        self._assert_resumes_from("2025-12-20", http_mocker)

    @HttpMocker()
    def test_datetime_state_resumes(self, http_mocker: HttpMocker):
        self._assert_resumes_from("2025-12-20T00:00:00Z", http_mocker)

    def _assert_resumes_from(self, cursor_value: str, http_mocker: HttpMocker) -> None:
        request = _notes_request("2025-12-20T00:00:00Z", _NOW)
        http_mocker.get(request, _notes_response(_notes_within("2025-12-20T00:00:00Z", _NOW)))

        output = _read_notes(StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": cursor_value}).build())

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        assert {message.record.data["id"] for message in output.records} == {"note-boundary-3"}


@freezegun.freeze_time(_NOW)
class TestNotesPagination(TestCase):
    _LAST_SLICE = _SLICE_BOUNDS[-1]

    def _mock_empty_slices_except_last(self, http_mocker: HttpMocker) -> None:
        for created_after, created_before in _SLICE_BOUNDS[:-1]:
            http_mocker.get(_notes_request(created_after, created_before), _notes_response([]))

    def _page(self, note_id: str, cursor: Optional[str], has_more: bool) -> HttpResponse:
        body = {"notes": [{"id": note_id, "created_at": "2026-01-12T09:00:00Z"}], "hasMore": has_more, "cursor": cursor}
        return HttpResponse(body=json.dumps(body), status_code=200)

    @HttpMocker()
    def test_follows_the_cursor_while_has_more_is_true(self, http_mocker: HttpMocker):
        self._mock_empty_slices_except_last(http_mocker)
        builder = GranolaRequestBuilder.notes_endpoint().with_created_after(self._LAST_SLICE[0]).with_created_before(self._LAST_SLICE[1])
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
        self._mock_empty_slices_except_last(http_mocker)
        request = _notes_request(*self._LAST_SLICE)
        http_mocker.get(request, self._page("note-only", cursor="stale-cursor", has_more=False))

        output = _read_notes()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["note-only"]
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(_NOW)
class TestNotesState(TestCase):
    @HttpMocker()
    def test_state_advances_to_the_latest_created_at_emitted(self, http_mocker: HttpMocker):
        for created_after, created_before in _SLICE_BOUNDS:
            http_mocker.get(
                _notes_request(created_after, created_before),
                _notes_response(_notes_within(created_after, created_before)),
            )

        output = _read_notes()

        assert output.errors == []
        assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2026-01-09T23:59:59Z"}

    @HttpMocker()
    def test_without_start_date_reads_the_last_730_days(self, http_mocker: HttpMocker):
        """The spec leaves `start_date` optional; the first slice then starts 730 days before now."""
        requests = []
        slice_start = datetime(2024, 1, 16, tzinfo=timezone.utc)
        now = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
        while slice_start <= now:
            slice_end = min(slice_start + timedelta(days=30) - timedelta(seconds=1), now)
            requests.append(_notes_request(slice_start.strftime("%Y-%m-%dT%H:%M:%SZ"), slice_end.strftime("%Y-%m-%dT%H:%M:%SZ")))
            slice_start = slice_end + timedelta(seconds=1)
        for request in requests:
            http_mocker.get(request, _notes_response([]))

        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors == []
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)
