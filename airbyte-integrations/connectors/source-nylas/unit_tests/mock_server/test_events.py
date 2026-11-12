# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_URL_BASE = "https://api.us.nylas.com/v3"
_API_KEY = "test_api_key"
_GRANT_ID = "grant-1"
_PRIMARY_CALENDAR_ID = "primary@example.com"
_HOLIDAY_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
_OTHER_CALENDAR_ID = "team@example.com"
# 2026-09-01T00:00:00Z / 2026-09-03T00:00:00Z as unix timestamps (the window from the issue)
_START = "1788220800"
_END = "1788393600"
_CONFIG = {
    "api_key": _API_KEY,
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}


def _request(path: str, query_params: Dict[str, str]) -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}{path}",
        query_params=query_params,
        headers={"Authorization": f"Bearer {_API_KEY}"},
    )


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": records}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return _request(
        f"/grants/{_GRANT_ID}/events",
        {"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _event(event_id: str, calendar_id: str) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": _GRANT_ID, "calendar_id": calendar_id, "updated_at": 1788300000, "object": "event"}


def _given_grant_with_calendars(http_mocker: HttpMocker, calendar_ids: List[str]) -> None:
    http_mocker.get(_request("/grants", {"limit": "50"}), _page([{"id": _GRANT_ID, "provider": "google"}]))
    http_mocker.get(
        _request(f"/grants/{_GRANT_ID}/calendars", {"limit": "50"}),
        _page([{"id": calendar_id, "grant_id": _GRANT_ID, "object": "calendar"} for calendar_id in calendar_ids]),
    )


def _read_events():
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync(self, http_mocker: HttpMocker) -> None:
        """A subscribed calendar (e.g. a Google holidays calendar) whose events endpoint returns 404
        must not fail the whole events stream; events from the user's other calendars are still emitted."""
        _given_grant_with_calendars(http_mocker, [_PRIMARY_CALENDAR_ID, _HOLIDAY_CALENDAR_ID, _OTHER_CALENDAR_ID])
        http_mocker.get(_events_request(_PRIMARY_CALENDAR_ID), _page([_event("evt-primary-1", _PRIMARY_CALENDAR_ID)]))
        holiday_events_request = _events_request(_HOLIDAY_CALENDAR_ID)
        http_mocker.get(
            holiday_events_request,
            HttpResponse(
                body=json.dumps({"request_id": "req-404", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(_events_request(_OTHER_CALENDAR_ID), _page([_event("evt-team-1", _OTHER_CALENDAR_ID)]))

        output = _read_events()

        assert sorted(record.record.data["id"] for record in output.records) == ["evt-primary-1", "evt-team-1"]
        assert not output.errors
        assert not any(log.log.level == Level.ERROR for log in output.logs)
        assert any(
            "Skipping events for this calendar" in log.log.message and log.log.level == Level.INFO for log in output.logs
        ), "expected a log explaining that the calendar was skipped"
        # the 404 is ignored, not retried
        http_mocker.assert_number_of_calls(holiday_events_request, 1)
