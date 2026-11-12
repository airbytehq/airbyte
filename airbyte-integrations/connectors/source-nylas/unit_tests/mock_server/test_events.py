# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"


def request(path: str, **params: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}/{path}",
        query_params={"limit": "50", **params},
        headers={"Authorization": "Bearer test-api-key"},
    )


@pytest.mark.parametrize("unavailable_first", [False, True])
@pytest.mark.parametrize("events", [[{"id": "event-a", "updated_at": 1788307200}], []])
def test_events_skips_calendar_returning_404(unavailable_first: bool, events: list[dict]) -> None:
    calendars = [
        {"id": "calendar-a", "is_primary": True},
        {"id": "calendar-b", "is_primary": False, "read_only": True, "name": "Public holidays"},
    ]
    if unavailable_first:
        calendars.reverse()
    with HttpMocker() as http:
        http.get(request("grants"), HttpResponse(json.dumps({"data": [{"id": "grant-1"}]}), 200))
        http.get(request("grants/grant-1/calendars"), HttpResponse(json.dumps({"data": calendars}), 200))
        normal = request("grants/grant-1/events", calendar_id="calendar-a", start="1788220800", end="1788393600")
        subscribed = request("grants/grant-1/events", calendar_id="calendar-b", start="1788220800", end="1788393600")
        http.get(normal, HttpResponse(json.dumps({"data": events}), 200))
        http.get(
            subscribed,
            HttpResponse(json.dumps({"request_id": "request-1", "error": {"type": "general", "message": "Not Found"}}), 404),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        assert not output.errors, output.get_formatted_error_message()
        assert [message.record.data["id"] for message in output.records] == [event["id"] for event in events]
        assert not any(message.log.level == Level.ERROR for message in output.logs)
        assert any("Skipping events for this calendar" in message.log.message for message in output.logs)
        http.assert_number_of_calls(normal, 1)
        http.assert_number_of_calls(subscribed, 1)
