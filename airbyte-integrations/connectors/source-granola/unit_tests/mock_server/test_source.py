# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the source's spec, check, discover, and authentication.

Granola has no test sandbox, so these pin the connector's contract with the platform:
the spec's required secret, the `check` stream, the catalog each stream advertises, and
the bearer token sent on every request.
"""

import json
import logging
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import GranolaRequestBuilder


_NOW = "2026-01-15T12:00:00Z"
_START_DATE = "2026-01-01"
_UPDATED_AFTER = "2026-01-01T00:00:00Z"
_API_KEY = "grn_test_key"
_LOGGER = logging.getLogger("airbyte")


def _config():
    return ConfigBuilder().with_api_key(_API_KEY).with_start_date(_START_DATE).build()


def _notes_request() -> GranolaRequestBuilder:
    return GranolaRequestBuilder.notes_endpoint().with_updated_after(_UPDATED_AFTER)


def _notes_response() -> HttpResponse:
    body = {"notes": [{"id": "note-1", "created_at": "2026-01-10T10:00:00Z"}], "hasMore": False}
    return HttpResponse(body=json.dumps(body), status_code=200)


class TestSpec(TestCase):
    def test_api_key_is_the_only_required_field_and_is_secret(self) -> None:
        spec = get_source(_config()).spec(_LOGGER).connectionSpecification

        assert spec["required"] == ["api_key"]
        assert spec["properties"]["api_key"]["airbyte_secret"] is True
        assert spec["properties"]["start_date"]["pattern"] == "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"


@freezegun.freeze_time(_NOW)
class TestCheck(TestCase):
    @HttpMocker()
    def test_check_succeeds_when_notes_can_be_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_notes_request().build(), _notes_response())

        status = get_source(_config()).check(_LOGGER, _config())

        assert status.status == Status.SUCCEEDED

    @HttpMocker()
    def test_check_fails_when_the_api_key_is_rejected(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_notes_request().build(), HttpResponse(body=json.dumps({"code": "UNAUTHORIZED"}), status_code=401))

        status = get_source(_config()).check(_LOGGER, _config())

        assert status.status == Status.FAILED
        assert "Granola rejected the API key" in status.message


@freezegun.freeze_time(_NOW)
class TestAuthentication(TestCase):
    @HttpMocker()
    def test_requests_send_the_api_key_as_a_bearer_token(self, http_mocker: HttpMocker) -> None:
        request = _notes_request().with_header("Authorization", f"Bearer {_API_KEY}").build()
        http_mocker.get(request, _notes_response())

        status = get_source(_config()).check(_LOGGER, _config())

        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(request, 1)


class TestDiscover(TestCase):
    def test_catalog_advertises_each_stream_with_its_sync_modes_and_keys(self) -> None:
        output = discover(get_source(_config()), _config())

        streams = {stream.name: stream for stream in output.catalog.catalog.streams}
        assert set(streams) == {"notes", "detailed_notes", "note_transcripts"}

        notes = streams["notes"]
        assert set(notes.supported_sync_modes) == {SyncMode.full_refresh, SyncMode.incremental}
        assert notes.source_defined_cursor is True
        assert notes.default_cursor_field == ["updated_at"]
        assert notes.source_defined_primary_key == [["id"]]

        detailed_notes = streams["detailed_notes"]
        assert detailed_notes.supported_sync_modes == [SyncMode.full_refresh]
        assert detailed_notes.source_defined_primary_key == [["id"]]

        # Transcript segments carry no stable identifier, so the stream has no primary key.
        note_transcripts = streams["note_transcripts"]
        assert note_transcripts.supported_sync_modes == [SyncMode.full_refresh]
        assert note_transcripts.source_defined_primary_key is None
