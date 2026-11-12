# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source


CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
ERROR = {"request_id": "request-id", "error": {"type": "general", "message": "Not Found"}}


def events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        f"{BASE_URL}/grants/grant-id/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": "1788220800", "end": "1788393600"},
    )


@pytest.mark.parametrize("status", [200, 404])
@pytest.mark.parametrize("event_ids", [[], ["event-b-1", "event-b-2"]])
def test_events_continue_after_calendar(status: int, event_ids: list[str], caplog: pytest.LogCaptureFixture) -> None:
    calendar_a_request = events_request("calendar-a")
    calendar_b_request = events_request("calendar-b")
    with HttpMocker() as mocker:
        mocker.get(
            HttpRequest(f"{BASE_URL}/grants", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "grant-id"}]})),
        )
        mocker.get(
            HttpRequest(f"{BASE_URL}/grants/grant-id/calendars", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "calendar-a"}, {"id": "calendar-b"}]})),
        )
        mocker.get(calendar_a_request, HttpResponse(json.dumps(ERROR if status == 404 else {"data": []}), status))
        mocker.get(
            calendar_b_request,
            HttpResponse(json.dumps({"data": [{"id": event_id, "updated_at": 1788307200} for event_id in event_ids]})),
        )

        output = read(get_source(CONFIG), CONFIG, CatalogBuilder().with_stream("events", SyncMode.incremental).build())

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == event_ids
        if status == 404:
            assert "The calendar identified by the request's calendar_id is skipped." in caplog.text
        mocker.assert_number_of_calls(calendar_a_request, 1)
        mocker.assert_number_of_calls(calendar_b_request, 1)


@pytest.mark.parametrize("endpoint,status", [("events", 403), ("calendars", 404)])
def test_other_errors_still_fail(endpoint: str, status: int) -> None:
    with HttpMocker() as mocker:
        mocker.get(
            HttpRequest(f"{BASE_URL}/grants", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "grant-id"}]})),
        )
        calendars_request = HttpRequest(f"{BASE_URL}/grants/grant-id/calendars", query_params={"limit": "50"})
        if endpoint == "calendars":
            mocker.get(calendars_request, HttpResponse(json.dumps(ERROR), status))
        else:
            mocker.get(calendars_request, HttpResponse(json.dumps({"data": [{"id": "calendar-a"}]})))
            mocker.get(events_request("calendar-a"), HttpResponse(json.dumps(ERROR), status))

        output = read(
            get_source(CONFIG),
            CONFIG,
            CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
            expecting_exception=True,
        )

        assert output.errors
        assert not output.records
