# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from unit_tests.conftest import get_source


_API_KEY = "test-api-key"
_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_OWN_CALENDAR_ID = "primary-calendar"
_SUBSCRIBED_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
_OTHER_CALENDAR_ID = "team-calendar"
# start_date / end_date below, as the epoch seconds the events stream sends in `start` / `end`
_START_EPOCH = "1788220800"
_END_EPOCH = "1788393600"

_CONFIG = {
    "api_key": _API_KEY,
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}

_NOT_FOUND_BODY = {"request_id": "req-404", "error": {"type": "general", "message": "Not Found"}}


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    # No `next_cursor`, so the paginator stops after this page.
    return HttpResponse(body=json.dumps({"request_id": "req", "data": records}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START_EPOCH, "end": _END_EPOCH},
    )


def _event(event_id: str, calendar_id: str) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": _GRANT_ID, "calendar_id": calendar_id, "updated_at": 1788300000, "object": "event"}


def _given_grant_with_calendars(http_mocker: HttpMocker, calendar_ids: List[str]) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants", query_params={"limit": "50"}),
        _page([{"id": _GRANT_ID, "provider": "google", "grant_status": "valid"}]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _page([{"id": calendar_id, "grant_id": _GRANT_ID, "object": "calendar"} for calendar_id in calendar_ids]),
    )


def _read_events(sync_mode: SyncMode):
    catalog = CatalogBuilder().with_stream("events", sync_mode).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog)


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync(sync_mode: SyncMode) -> None:
    """A calendar whose events endpoint returns 404 (e.g. a subscribed holidays calendar) must not fail the whole
    events stream: events from the grant's other calendars are still emitted, and each calendar is requested once."""
    with HttpMocker() as http_mocker:
        _given_grant_with_calendars(http_mocker, [_OWN_CALENDAR_ID, _SUBSCRIBED_CALENDAR_ID, _OTHER_CALENDAR_ID])
        http_mocker.get(_events_request(_OWN_CALENDAR_ID), _page([_event("event-1", _OWN_CALENDAR_ID)]))
        subscribed_calendar_events_request = _events_request(_SUBSCRIBED_CALENDAR_ID)
        http_mocker.get(subscribed_calendar_events_request, HttpResponse(body=json.dumps(_NOT_FOUND_BODY), status_code=404))
        http_mocker.get(_events_request(_OTHER_CALENDAR_ID), _page([_event("event-2", _OTHER_CALENDAR_ID)]))

        output = _read_events(sync_mode)

        assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        http_mocker.assert_number_of_calls(subscribed_calendar_events_request, 1)
