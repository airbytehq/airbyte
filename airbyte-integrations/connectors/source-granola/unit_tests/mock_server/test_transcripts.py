# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for Granola's oversized-transcript behavior.

`GET /v1/notes/{note_id}?include=transcript` answers `413 TRANSCRIPT_TOO_LARGE` when a
transcript is too large to be returned inline, which used to be retried until the whole
`detailed_notes` sync failed. `detailed_notes` now skips those notes, and `note_transcripts`
replicates the transcript from the paged `GET /v1/notes/{note_id}/transcript` endpoint.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import GranolaRequestBuilder


_NOW = "2026-01-15T12:00:00Z"
_START_DATE = "2026-01-01"
# A start date within one 30-day step keeps the parent stream to a single slice, so each
# note is partitioned exactly once and the child request assertions stay unambiguous.
_ONLY_SLICE = ("2026-01-01T00:00:00Z", _NOW)

_TRANSCRIPT_TOO_LARGE = {
    "code": "TRANSCRIPT_TOO_LARGE",
    "message": "Transcript is too large to return inline. Retrieve it in pages from /v1/notes/{note_id}/transcript.",
}


def _note(note_id: str) -> Dict[str, Any]:
    return {"id": note_id, "title": f"Meeting {note_id}", "created_at": "2026-01-10T10:00:00Z"}


def _notes_request() -> HttpRequest:
    created_after, created_before = _ONLY_SLICE
    return GranolaRequestBuilder.notes_endpoint().with_created_after(created_after).with_created_before(created_before).build()


def _notes_response(*note_ids: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"notes": [_note(note_id) for note_id in note_ids], "hasMore": False}), status_code=200)


def _segment(text: str) -> Dict[str, Any]:
    return {
        "speaker": {"source": "microphone"},
        "text": text,
        "start_time": "2026-01-10T10:00:00Z",
        "end_time": "2026-01-10T10:00:05Z",
    }


def _transcript_response(text: str, cursor: Optional[str] = None) -> HttpResponse:
    body = {"transcript": [_segment(text)], "hasMore": cursor is not None, "cursor": cursor}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().with_start_date(_START_DATE).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def _record_ids(output: EntrypointOutput) -> List[str]:
    return [message.record.data["id"] for message in output.records]


@freezegun.freeze_time(_NOW)
class TestOversizedTranscripts(TestCase):
    @HttpMocker()
    def test_detailed_notes_skips_notes_whose_transcript_is_too_large(self, http_mocker: HttpMocker):
        """A 413 skips that one note instead of failing the stream, and is not retried."""
        http_mocker.get(_notes_request(), _notes_response("note-small", "note-large"))
        http_mocker.get(
            GranolaRequestBuilder.note_endpoint("note-small").with_include("transcript").build(),
            HttpResponse(body=json.dumps({**_note("note-small"), "transcript": [_segment("hello")]}), status_code=200),
        )
        oversized_request = GranolaRequestBuilder.note_endpoint("note-large").with_include("transcript").build()
        http_mocker.get(oversized_request, HttpResponse(body=json.dumps(_TRANSCRIPT_TOO_LARGE), status_code=413))

        output = _read("detailed_notes")

        assert output.errors == []
        assert _record_ids(output) == ["note-small"]
        http_mocker.assert_number_of_calls(oversized_request, 1)
        # The CDK emits an IGNORE filter's message at INFO, so the docs tell operators to
        # grep for it rather than watch for a warning.
        skip_logs = [message.log for message in output.logs if "transcript is too large" in message.log.message]
        assert [log.level for log in skip_logs] == [Level.INFO]

    @HttpMocker()
    def test_note_transcripts_follows_the_transcript_cursor(self, http_mocker: HttpMocker):
        """Transcript pages are requested with `page_size=100` and the returned cursor."""
        http_mocker.get(_notes_request(), _notes_response("note-large"))
        first_page = GranolaRequestBuilder.transcript_endpoint("note-large").build()
        second_page = GranolaRequestBuilder.transcript_endpoint("note-large").with_cursor("cursor-2").build()
        http_mocker.get(first_page, _transcript_response("page one", cursor="cursor-2"))
        http_mocker.get(second_page, _transcript_response("page two"))

        output = _read("note_transcripts")

        assert output.errors == []
        assert [message.record.data["text"] for message in output.records] == ["page one", "page two"]
        assert all(message.record.data["note_id"] == "note-large" for message in output.records)
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_note_transcripts_skips_notes_without_a_transcript(self, http_mocker: HttpMocker):
        """A 404 on the transcript endpoint skips that note instead of failing the stream."""
        http_mocker.get(_notes_request(), _notes_response("note-a", "note-gone"))
        http_mocker.get(GranolaRequestBuilder.transcript_endpoint("note-a").build(), _transcript_response("note-a text"))
        missing = GranolaRequestBuilder.transcript_endpoint("note-gone").build()
        http_mocker.get(missing, HttpResponse(body=json.dumps({"code": "NOT_FOUND"}), status_code=404))

        output = _read("note_transcripts")

        assert output.errors == []
        assert [message.record.data["note_id"] for message in output.records] == ["note-a"]
        http_mocker.assert_number_of_calls(missing, 1)

    @HttpMocker()
    def test_note_transcripts_requests_a_transcript_per_note(self, http_mocker: HttpMocker):
        http_mocker.get(_notes_request(), _notes_response("note-a", "note-b"))
        for note_id in ("note-a", "note-b"):
            http_mocker.get(
                GranolaRequestBuilder.transcript_endpoint(note_id).build(),
                _transcript_response(f"{note_id} text"),
            )

        output = _read("note_transcripts")

        assert output.errors == []
        assert sorted(message.record.data["note_id"] for message in output.records) == ["note-a", "note-b"]
