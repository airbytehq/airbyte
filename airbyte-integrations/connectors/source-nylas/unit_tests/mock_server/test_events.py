# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Mapping

import pytest
from conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


API_KEY = "test_api_key"
CONFIG = {"api_key": API_KEY, "api_server": "us", "start_date": "2026-09-01T00:00:00Z", "end_date": "2026-09-03T00:00:00Z"}
GRANT_ID = "grant-1"
PRIMARY_CALENDAR = "primary@example.com"
HOLIDAY_CALENDAR = "en.usa#holiday@group.v.calendar.google.com"


def _request(path: str, params: Mapping[str, str]) -> HttpRequest:
    return HttpRequest(
        url=f"https://api.us.nylas.com/v3/{path}",
        query_params=dict(params),
        headers={"Authorization": f"Bearer {API_KEY}"},
    )


def _page(records: list[Mapping[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": records}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return _request(
        f"grants/{GRANT_ID}/events",
        {"limit": "50", "calendar_id": calendar_id, "start": "1788220800", "end": "1788393600"},
    )


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_events_read_skips_calendar_that_returns_404_and_syncs_other_calendars(sync_mode: SyncMode) -> None:
    holiday_events_request = _events_request(HOLIDAY_CALENDAR)
    with HttpMocker() as http:
        http.get(_request("grants", {"limit": "50"}), _page([{"id": GRANT_ID}]))
        http.get(
            _request(f"grants/{GRANT_ID}/calendars", {"limit": "50"}),
            _page([{"id": HOLIDAY_CALENDAR, "grant_id": GRANT_ID}, {"id": PRIMARY_CALENDAR, "grant_id": GRANT_ID}]),
        )
        http.get(
            holiday_events_request,
            HttpResponse(
                body=json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http.get(
            _events_request(PRIMARY_CALENDAR),
            _page([{"id": "event-1", "calendar_id": PRIMARY_CALENDAR, "grant_id": GRANT_ID, "updated_at": 1788300000}]),
        )

        catalog = CatalogBuilder().with_stream("events", sync_mode).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == ["event-1"]
        assert not output.errors
        assert not any(log.log.level == Level.ERROR for log in output.logs)
        assert any(
            log.log.message
            == f"Skipping events of a calendar that Nylas returned 404 Not Found for: https://api.us.nylas.com/v3/grants/{GRANT_ID}/events"
            for log in output.logs
        )
        http.assert_number_of_calls(holiday_events_request, 1)
