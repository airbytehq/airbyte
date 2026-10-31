# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `events` stream.

Nylas returns `404 Not Found` from `GET /v3/grants/{grant}/events?calendar_id=...`
for some calendars listed by the `calendars` stream (eg subscribed public holiday
calendars). One such calendar must not fail the whole stream: events from the
grant's other calendars should still sync.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_PRIMARY_CALENDAR_ID = "primary@example.com"
_HOLIDAYS_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"

_CONFIG = {
    "api_key": "api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_START = "1788220800"
_END = "1788393600"


def _page(data: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": data}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _event(event_id: str, calendar_id: str) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": _GRANT_ID, "calendar_id": calendar_id, "updated_at": 1788300000}


def _mock_parents(http_mocker: HttpMocker) -> None:
    http_mocker.get(HttpRequest(f"{_BASE_URL}/grants", query_params={"limit": "50"}), _page([{"id": _GRANT_ID}]))
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _page(
            [
                {"id": _PRIMARY_CALENDAR_ID, "grant_id": _GRANT_ID, "name": "Primary"},
                {"id": _HOLIDAYS_CALENDAR_ID, "grant_id": _GRANT_ID, "name": "Holidays in United States", "read_only": True},
            ]
        ),
    )


def _read_events() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class EventsStreamTest(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_sync(self, http_mocker: HttpMocker) -> None:
        _mock_parents(http_mocker)
        http_mocker.get(_events_request(_PRIMARY_CALENDAR_ID), _page([_event("event-1", _PRIMARY_CALENDAR_ID)]))
        http_mocker.get(
            _events_request(_HOLIDAYS_CALENDAR_ID),
            HttpResponse(
                body=json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )

        output = _read_events()

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["event-1"]

    @HttpMocker()
    def test_events_from_all_calendars_are_read(self, http_mocker: HttpMocker) -> None:
        _mock_parents(http_mocker)
        http_mocker.get(_events_request(_PRIMARY_CALENDAR_ID), _page([_event("event-1", _PRIMARY_CALENDAR_ID)]))
        http_mocker.get(_events_request(_HOLIDAYS_CALENDAR_ID), _page([_event("event-2", _HOLIDAYS_CALENDAR_ID)]))

        output = _read_events()

        assert output.errors == []
        assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2"]
