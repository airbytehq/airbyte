# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source


_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_OWNED_CALENDAR_ID = "primary@example.com"
_SUBSCRIBED_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
# 2026-09-01T00:00:00Z and 2026-09-03T00:00:00Z as epoch seconds
_START = "1788220800"
_END = "1788393600"

_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}


def _json_response(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _given_grant_with_calendars(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants", query_params={"limit": "50"}),
        _json_response({"data": [{"id": _GRANT_ID, "provider": "google"}]}),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _json_response(
            {
                "data": [
                    {"id": _SUBSCRIBED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": False, "read_only": True},
                    {"id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": True, "read_only": False},
                ]
            }
        ),
    )


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_given_calendar_returns_404_when_read_then_skip_calendar_and_sync_other_calendars(self, http_mocker: HttpMocker) -> None:
        _given_grant_with_calendars(http_mocker)
        subscribed_calendar_request = _events_request(_SUBSCRIBED_CALENDAR_ID)
        owned_calendar_request = _events_request(_OWNED_CALENDAR_ID)
        http_mocker.get(
            subscribed_calendar_request,
            _json_response({"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}, status_code=404),
        )
        http_mocker.get(
            owned_calendar_request,
            _json_response(
                {
                    "data": [
                        {"id": "event-1", "calendar_id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "updated_at": 1788300000},
                        {"id": "event-2", "calendar_id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "updated_at": 1788310000},
                    ]
                }
            ),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == ["event-1", "event-2"]
        assert not output.errors
        assert not any(log.log.level == Level.ERROR for log in output.logs)
        assert any("calendar was not found or is not accessible" in log.log.message and "404" in log.log.message for log in output.logs), (
            "expected an informational log explaining why the calendar was skipped"
        )
        http_mocker.assert_number_of_calls(subscribed_calendar_request, 1)
        http_mocker.assert_number_of_calls(owned_calendar_request, 1)
