# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
GRANT_ID = "grant-1"
HOLIDAYS_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
NOT_FOUND_BODY = {"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}


def _events_request(calendar_id):
    return HttpRequest(
        url=f"{BASE_URL}/grants/{GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": "1788220800", "end": "1788393600"},
    )


def _event(event_id, calendar_id):
    return {"id": event_id, "calendar_id": calendar_id, "grant_id": GRANT_ID, "updated_at": 1788300000}


def test_events_skips_calendar_that_returns_404_and_reads_the_other_calendars():
    calendar_ids = ["primary@example.com", HOLIDAYS_CALENDAR_ID, "team@example.com"]
    holidays_request = _events_request(HOLIDAYS_CALENDAR_ID)
    primary_request = _events_request("primary@example.com")
    team_request = _events_request("team@example.com")

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{BASE_URL}/grants", query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": GRANT_ID}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{BASE_URL}/grants/{GRANT_ID}/calendars", query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": calendar_id, "grant_id": GRANT_ID} for calendar_id in calendar_ids]})),
        )
        http_mocker.get(primary_request, HttpResponse(body=json.dumps({"data": [_event("event-primary", "primary@example.com")]})))
        http_mocker.get(holidays_request, HttpResponse(body=json.dumps(NOT_FOUND_BODY), status_code=404))
        http_mocker.get(team_request, HttpResponse(body=json.dumps({"data": [_event("event-team", "team@example.com")]})))

        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        http_mocker.assert_number_of_calls(primary_request, 1)
        http_mocker.assert_number_of_calls(holidays_request, 1)
        http_mocker.assert_number_of_calls(team_request, 1)

    assert not output.errors
    assert sorted(record.record.data["id"] for record in output.records) == ["event-primary", "event-team"]
    assert not any(log.log.level == "ERROR" for log in output.logs)
    skip_logs = [log.log.message for log in output.logs if "Skipping this calendar" in log.log.message]
    assert len(skip_logs) == 1
