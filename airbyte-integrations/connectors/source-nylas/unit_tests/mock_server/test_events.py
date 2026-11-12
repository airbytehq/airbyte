# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


def test_events_skips_inaccessible_calendar() -> None:
    config = {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }
    base_url = "https://api.us.nylas.com/v3/grants"
    holiday_calendar_id = "en.usa#holiday@group.v.calendar.google.com"
    primary_calendar_id = "primary-calendar"
    events = [
        {"id": "event-1", "calendar_id": primary_calendar_id, "updated_at": 1788220800},
        {"id": "event-2", "calendar_id": primary_calendar_id, "updated_at": 1788307200},
    ]
    holiday_request = HttpRequest(
        url=f"{base_url}/grant-1/events",
        query_params={"limit": "50", "calendar_id": holiday_calendar_id, "start": "1788220800", "end": "1788393600"},
    )
    primary_request = HttpRequest(
        url=f"{base_url}/grant-1/events",
        query_params={"limit": "50", "calendar_id": primary_calendar_id, "start": "1788220800", "end": "1788393600"},
    )
    with HttpMocker() as http:
        http.get(
            HttpRequest(url=base_url, query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "grant-1"}]}), 200),
        )
        http.get(
            HttpRequest(url=f"{base_url}/grant-1/calendars", query_params={"limit": "50"}),
            HttpResponse(
                json.dumps(
                    {
                        "data": [
                            {"id": holiday_calendar_id, "name": "US Holidays", "is_primary": False},
                            {"id": primary_calendar_id, "name": "Primary", "is_primary": True},
                        ]
                    }
                ),
                200,
            ),
        )
        http.get(
            holiday_request,
            HttpResponse(json.dumps({"request_id": "request-1", "error": {"type": "general", "message": "Not Found"}}), 404),
        )
        http.get(primary_request, HttpResponse(json.dumps({"data": events}), 200))

        catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

        assert output.errors == []
        assert [log.log.message for log in output.logs if log.log.level == Level.ERROR] == []
        assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2"]
        http.assert_number_of_calls(holiday_request, 1)
        http.assert_number_of_calls(primary_request, 1)
