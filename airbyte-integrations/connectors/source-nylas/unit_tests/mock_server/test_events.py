# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime

import pytest
from conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
CALENDARS = ["public-holidays@group.v.calendar.google.com", "calendar-b"]


def response(data):
    return HttpResponse(body=json.dumps({"data": data}))


def event_request(calendar):
    return HttpRequest(
        url=f"{BASE_URL}/grants/grant-a/events",
        query_params={
            "calendar_id": calendar,
            "limit": "50",
            "start": str(int(datetime.fromisoformat(CONFIG["start_date"]).timestamp())),
            "end": str(int(datetime.fromisoformat(CONFIG["end_date"]).timestamp())),
        },
    )


@pytest.mark.parametrize("status", [200, 404, 401, 500])
@pytest.mark.parametrize("empty", [False, True])
def test_events_calendar_errors(status, empty, recorded_sleeps):
    events = [] if empty else [{"id": name, "updated_at": 1788307200} for name in ["event-b-1", "event-b-2"]]
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    targets = [event_request(calendar) for calendar in CALENDARS]
    with HttpMocker() as http:
        http.get(HttpRequest(url=f"{BASE_URL}/grants", query_params={"limit": "50"}), response([{"id": "grant-a"}]))
        http.get(
            HttpRequest(url=f"{BASE_URL}/grants/grant-a/calendars", query_params={"limit": "50"}),
            response([{"id": calendar} for calendar in CALENDARS]),
        )
        http.get(
            targets[0],
            response([])
            if status == 200
            else HttpResponse(
                body=json.dumps({"request_id": "request-a", "error": {"type": "general", "message": "Not Found"}}),
                status_code=status,
            ),
        )
        http.get(targets[1], response(events))

        output = read(get_source(CONFIG), CONFIG, catalog)

        if status in [401, 500]:
            assert output.errors
            assert output.get_stream_statuses("events")[-1].value != "COMPLETE"
            return

        assert not output.errors
        assert sorted(message.record.data["id"] for message in output.records) == sorted(event["id"] for event in events)
        assert output.get_stream_statuses("events")[-1].value == "COMPLETE"
        assert not any(message.log.level == Level.ERROR for message in output.logs)
        if status == 404:
            assert any(
                message.log.level in [Level.INFO, Level.WARN]
                and "Skipping events for a calendar whose events endpoint returned 404" in message.log.message
                and f"{BASE_URL}/grants/grant-a/events" in message.log.message
                for message in output.logs
            )
        for target in targets:
            http.assert_number_of_calls(target, 1)
