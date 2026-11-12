# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `events` stream, which reads one grant's events calendar by calendar."""

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_API_URL = "https://api.us.nylas.com/v3"
_HEADERS = {"Authorization": "Bearer test-api-key"}
_GRANT_ID = "grant-1"
_HOLIDAY_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
_PRIMARY_CALENDAR_ID = "user@example.com"
_TEAM_CALENDAR_ID = "team@group.calendar.google.com"


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_API_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": "1788220800", "end": "1788393600"},
        headers=_HEADERS,
    )


def _events_response(calendar_id: str, *event_ids: str) -> HttpResponse:
    events = [{"id": event_id, "calendar_id": calendar_id, "grant_id": _GRANT_ID, "updated_at": 1788300000} for event_id in event_ids]
    return HttpResponse(body=json.dumps({"request_id": "req-1", "data": events}), status_code=200)


def _given_grant_with_calendars(http_mocker: HttpMocker, *calendar_ids: str) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_API_URL}/grants", query_params={"limit": "50"}, headers=_HEADERS),
        HttpResponse(body=json.dumps({"request_id": "req-1", "data": [{"id": _GRANT_ID, "provider": "google"}]}), status_code=200),
    )
    calendars = [{"id": calendar_id, "grant_id": _GRANT_ID} for calendar_id in calendar_ids]
    http_mocker.get(
        HttpRequest(url=f"{_API_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}, headers=_HEADERS),
        HttpResponse(body=json.dumps({"request_id": "req-1", "data": calendars}), status_code=200),
    )


def _read_events() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def test_calendar_answering_404_is_skipped_and_other_calendars_still_sync() -> None:
    """Nylas lists a subscribed calendar but answers 404 for its events; the other calendars must still sync."""
    with HttpMocker() as http_mocker:
        _given_grant_with_calendars(http_mocker, _HOLIDAY_CALENDAR_ID, _PRIMARY_CALENDAR_ID, _TEAM_CALENDAR_ID)
        holiday_request = _events_request(_HOLIDAY_CALENDAR_ID)
        primary_request = _events_request(_PRIMARY_CALENDAR_ID)
        team_request = _events_request(_TEAM_CALENDAR_ID)
        http_mocker.get(
            holiday_request,
            HttpResponse(
                body=json.dumps({"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(primary_request, _events_response(_PRIMARY_CALENDAR_ID, "event-1", "event-2"))
        http_mocker.get(team_request, _events_response(_TEAM_CALENDAR_ID, "event-3"))

        output = _read_events()

        assert output.errors == []
        assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2", "event-3"]
        # The 404 is not retried, and each readable calendar is requested exactly once.
        http_mocker.assert_number_of_calls(holiday_request, 1)
        http_mocker.assert_number_of_calls(primary_request, 1)
        http_mocker.assert_number_of_calls(team_request, 1)
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The skip is reported at INFO with the grant it happened under, so the gap is visible in the sync logs.
        assert [log.log.message for log in output.logs if "404" in log.log.message] == [
            "Nylas returned 404 (Not Found) for the events of a calendar listed under "
            f"{_API_URL}/grants/{_GRANT_ID}/events. Skipping that calendar and continuing with the other calendars."
        ]
