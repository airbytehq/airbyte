# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for the `events` stream, which reads one partition per (grant, calendar)."""

import json
from typing import Any, Dict, List

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.us.nylas.com"
_GRANT_ID = "grant-1"
_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
# `start_date` and `end_date` as the epoch seconds the `events` requests carry.
_START = "1788220800"
_END = "1788393600"

_PRIMARY_CALENDAR = "primary@example.com"
_HOLIDAY_CALENDAR = "en.usa#holiday@group.v.calendar.google.com"
_TEAM_CALENDAR = "team@group.calendar.google.com"

_NOT_FOUND_BODY = {"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}


def _response(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req-1", "data": records}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}/v3/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _mock_grant_and_calendars(http_mocker: HttpMocker, calendar_ids: List[str]) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/v3/grants", query_params={"limit": "50"}),
        _response([{"id": _GRANT_ID, "provider": "google"}]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/v3/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _response([{"id": calendar_id, "grant_id": _GRANT_ID} for calendar_id in calendar_ids]),
    )


def _read_events() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync() -> None:
    with HttpMocker() as http_mocker:
        _mock_grant_and_calendars(http_mocker, [_PRIMARY_CALENDAR, _HOLIDAY_CALENDAR, _TEAM_CALENDAR])
        http_mocker.get(
            _events_request(_PRIMARY_CALENDAR),
            _response([{"id": "event-primary", "calendar_id": _PRIMARY_CALENDAR, "updated_at": 1788300000}]),
        )
        holiday_request = _events_request(_HOLIDAY_CALENDAR)
        http_mocker.get(holiday_request, HttpResponse(body=json.dumps(_NOT_FOUND_BODY), status_code=404))
        http_mocker.get(
            _events_request(_TEAM_CALENDAR),
            _response([{"id": "event-team", "calendar_id": _TEAM_CALENDAR, "updated_at": 1788310000}]),
        )

        output = _read_events()

        assert sorted(record.record.data["id"] for record in output.records) == ["event-primary", "event-team"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The 404 is not retried: the skipped calendar is requested exactly once.
        http_mocker.assert_number_of_calls(holiday_request, 1)
        skip_logs = [log.log.message for log in output.logs if "Skipping events for one calendar" in log.log.message]
        assert len(skip_logs) == 1
        assert f"/v3/grants/{_GRANT_ID}/events" in skip_logs[0]
