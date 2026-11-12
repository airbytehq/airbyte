# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `events` stream on `source-nylas`.

`GET /v3/grants/{grant_id}/events` is partitioned per grant and per calendar
(`calendar_id` query param) and bounded by the configured `start`/`end` window
(Unix seconds). Nylas returns 404 for some calendars the `calendars` stream
lists, such as Google subscribed holiday calendars; such a calendar must be
skipped without failing the stream so events from the other calendars sync.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder


_STREAM_NAME = "events"
_GRANT_ID = "grant-1"
_START = 1788220800  # 2026-09-01T00:00:00Z
_END = 1788393600  # 2026-09-03T00:00:00Z


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"request_id": "req", "data": records}), 200)


def _not_found() -> HttpResponse:
    return HttpResponse(json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}), 404)


def _event(event_id: str, calendar_id: str) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": _GRANT_ID, "calendar_id": calendar_id, "title": event_id, "updated_at": _START + 3600}


def _events_request(calendar_id: str):
    return (
        NylasRequestBuilder.events_endpoint(_GRANT_ID)
        .with_limit(50)
        .with_query_param("calendar_id", calendar_id)
        .with_query_param("start", _START)
        .with_query_param("end", _END)
        .build()
    )


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config, catalog)


class TestEvents(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_sync(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(NylasRequestBuilder.grants_endpoint().with_limit(50).build(), _page([{"id": _GRANT_ID}]))
        http_mocker.get(
            NylasRequestBuilder.calendars_endpoint(_GRANT_ID).with_limit(50).build(),
            _page(
                [
                    {"id": "primary@example.com", "grant_id": _GRANT_ID, "is_owned_by_user": True},
                    {"id": "en.usa#holiday@group.v.calendar.google.com", "grant_id": _GRANT_ID, "is_owned_by_user": False, "read_only": True},
                    {"id": "work@example.com", "grant_id": _GRANT_ID, "is_owned_by_user": True},
                ]
            ),
        )
        http_mocker.get(_events_request("primary@example.com"), _page([_event("evt-1", "primary@example.com")]))
        holiday_request = _events_request("en.usa#holiday@group.v.calendar.google.com")
        http_mocker.get(holiday_request, _not_found())
        http_mocker.get(_events_request("work@example.com"), _page([_event("evt-2", "work@example.com")]))

        output = _read()

        assert sorted(r.record.data["id"] for r in output.records) == ["evt-1", "evt-2"]
        assert not output.errors
        # A 404 is not retried: the calendar is requested exactly once, then skipped.
        http_mocker.assert_number_of_calls(holiday_request, 1)

    @HttpMocker()
    def test_server_error_on_a_calendar_still_fails_the_stream(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(NylasRequestBuilder.grants_endpoint().with_limit(50).build(), _page([{"id": _GRANT_ID}]))
        http_mocker.get(
            NylasRequestBuilder.calendars_endpoint(_GRANT_ID).with_limit(50).build(),
            _page([{"id": "primary@example.com", "grant_id": _GRANT_ID}]),
        )
        http_mocker.get(
            _events_request("primary@example.com"),
            HttpResponse(json.dumps({"error": {"type": "general", "message": "Forbidden"}}), 403),
        )

        output = _read()

        assert output.records == []
        assert output.errors
