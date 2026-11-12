# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


CONFIG = {
    "api_key": "k",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"


@pytest.mark.parametrize("status", [200, 404])
def test_events_continue_after_unavailable_or_empty_calendar(status: int) -> None:
    with HttpMocker() as http:
        http.get(
            HttpRequest(url=f"{BASE_URL}/grants", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "grant"}]}), 200),
        )
        http.get(
            HttpRequest(url=f"{BASE_URL}/grants/grant/calendars", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "calendar-a"}, {"id": "calendar-b"}]}), 200),
        )
        requests = {
            calendar: HttpRequest(
                url=f"{BASE_URL}/grants/grant/events",
                query_params={
                    "calendar_id": calendar,
                    "start": "1788220800",
                    "end": "1788393600",
                    "limit": "50",
                },
            )
            for calendar in ("calendar-a", "calendar-b")
        }
        body = {"request_id": "request", "error": {"type": "general", "message": "Not Found"}} if status == 404 else {"data": []}
        http.get(requests["calendar-a"], HttpResponse(json.dumps(body), status))
        http.get(
            requests["calendar-b"],
            HttpResponse(json.dumps({"data": [{"id": "event-b", "updated_at": 1788307200}]}), 200),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        assert not output.errors
        assert not any(log.log.level == Level.ERROR for log in output.logs)
        assert [record.record.data["id"] for record in output.records] == ["event-b"]
        http.assert_number_of_calls(requests["calendar-a"], 1)
        http.assert_number_of_calls(requests["calendar-b"], 1)
