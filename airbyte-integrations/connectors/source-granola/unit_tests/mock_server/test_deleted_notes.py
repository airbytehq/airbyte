# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `deleted_notes` stream, which reads `GET /v1/audit`
filtered to `action=document.hard_deleted`.

The audit endpoint is Enterprise-only and authenticates with a dedicated Audit
API key; a normal notes key gets a 404. These tests cover the happy path
(pagination over `cursor`/`hasMore`, `note_id` lifted from `data.documentId`,
occurred_* slice bounds sent on the request) and the 404 -> config_error path.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import GranolaRequestBuilder


_NOW = "2026-01-15T12:00:00Z"
_START_DATE = "2026-01-01"
_STREAM_NAME = "deleted_notes"

# deleted_notes has no step, so the whole range is a single slice.
_SLICE = ("2026-01-01T00:00:00Z", _NOW)


def _audit_event(event_id: str, note_id: str, occurred_at: str = "2026-01-10T10:00:00Z") -> Dict[str, Any]:
    return {
        "id": event_id,
        "object": "audit_event",
        "action": "document.hard_deleted",
        "occurred_at": occurred_at,
        "collected_at": "2026-01-10T10:00:01Z",
        "actor": {"type": "user"},
        "data": {"documentId": note_id},
    }


def _audit_request(occurred_after: str, occurred_before: str, cursor: Optional[str] = None) -> HttpRequest:
    builder = GranolaRequestBuilder.audit_endpoint().with_occurred_after(occurred_after).with_occurred_before(occurred_before)
    if cursor:
        builder.with_cursor(cursor)
    return builder.build()


def _audit_response(events: List[Dict[str, Any]], cursor: Optional[str] = None) -> HttpResponse:
    return HttpResponse(body=json.dumps({"events": events, "hasMore": cursor is not None, "cursor": cursor}), status_code=200)


def _read_deleted_notes() -> EntrypointOutput:
    config = ConfigBuilder().with_audit_api_key("test-audit-key").with_start_date(_START_DATE).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


@freezegun.freeze_time(_NOW)
class TestDeletedNotes(TestCase):
    @HttpMocker()
    def test_reads_all_pages_and_lifts_note_id(self, http_mocker: HttpMocker):
        """Two pages of audit events, each yielding a record whose note_id is data.documentId."""
        occurred_after, occurred_before = _SLICE
        first_page = _audit_request(occurred_after, occurred_before)
        second_page = _audit_request(occurred_after, occurred_before, cursor="c1")
        http_mocker.get(first_page, _audit_response([_audit_event("aud_1", "note-deleted-1")], cursor="c1"))
        http_mocker.get(second_page, _audit_response([_audit_event("aud_2", "note-deleted-2")]))

        output = _read_deleted_notes()

        assert output.errors == []
        assert [message.record.data["note_id"] for message in output.records] == ["note-deleted-1", "note-deleted-2"]
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_request_carries_action_bounds_and_page_size(self, http_mocker: HttpMocker):
        """The single slice is sent as occurred_after/occurred_before with the documented max page size."""
        occurred_after, occurred_before = _SLICE
        request = _audit_request(occurred_after, occurred_before)
        http_mocker.get(request, _audit_response([]))

        output = _read_deleted_notes()

        assert output.errors == []
        # The builder builds action/page_size/occurred_* into the matched URL, so the
        # call assertion already proves the request carried them.
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_404_without_an_audit_key_is_a_config_error(self, http_mocker: HttpMocker):
        """A notes key gets 404 on /v1/audit; the stream fails with a config error naming the Audit API key."""
        occurred_after, occurred_before = _SLICE
        http_mocker.get(
            _audit_request(occurred_after, occurred_before),
            HttpResponse(body=json.dumps({"code": "NOT_FOUND"}), status_code=404),
        )

        config = ConfigBuilder().with_start_date(_START_DATE).build()
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors != []
        config_errors = [message.trace.error for message in output.errors if message.trace.error.failure_type == FailureType.config_error]
        assert config_errors
        assert any("Audit API key" in (error.message or "") for error in config_errors)


@freezegun.freeze_time(_NOW)
class TestNotesErrorHandling(TestCase):
    @HttpMocker()
    def test_401_is_a_config_error_naming_the_api_key(self, http_mocker: HttpMocker):
        self._assert_unauthorized_is_config_error(401, http_mocker)

    @HttpMocker()
    def test_403_is_a_config_error_naming_the_api_key(self, http_mocker: HttpMocker):
        self._assert_unauthorized_is_config_error(403, http_mocker)

    def _assert_unauthorized_is_config_error(self, status_code: int, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            GranolaRequestBuilder.notes_endpoint().with_created_after(_START_DATE + "T00:00:00Z").with_created_before(_NOW).build(),
            HttpResponse(body=json.dumps({"error": {"code": "INVALID_API_KEY"}}), status_code=status_code),
        )

        config = ConfigBuilder().with_start_date(_START_DATE).build()
        catalog = CatalogBuilder().with_stream("notes", SyncMode.incremental).build()
        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors != []
        config_errors = [message.trace.error for message in output.errors if message.trace.error.failure_type == FailureType.config_error]
        assert config_errors
        assert any("API key" in (error.message or "") for error in config_errors)
