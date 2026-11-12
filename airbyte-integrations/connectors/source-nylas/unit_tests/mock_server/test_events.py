# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test_api_key"
_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_OWNED_CALENDAR_ID = "primary-calendar@example.com"
_SUBSCRIBED_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
# 2026-09-01T00:00:00Z and 2026-09-03T00:00:00Z as unix seconds
_START = "1788220800"
_END = "1788393600"
_CONFIG = {
    "api_key": _API_KEY,
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}


def _json(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _given_grant_and_calendars(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants", query_params={"limit": "50"}),
        _json({"request_id": "r1", "data": [{"id": _GRANT_ID, "provider": "google"}]}),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _json(
            {
                "request_id": "r2",
                "data": [
                    {"id": _SUBSCRIBED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": False, "read_only": True},
                    {"id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": True, "read_only": False},
                ],
            }
        ),
    )


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_404_on_one_calendar_is_skipped_and_other_calendars_still_sync(self, http_mocker: HttpMocker) -> None:
        _given_grant_and_calendars(http_mocker)
        subscribed_calendar_request = _events_request(_SUBSCRIBED_CALENDAR_ID)
        owned_calendar_request = _events_request(_OWNED_CALENDAR_ID)
        http_mocker.get(
            subscribed_calendar_request,
            _json({"request_id": "r3", "error": {"type": "general", "message": "Not Found"}}, status_code=404),
        )
        http_mocker.get(
            owned_calendar_request,
            _json(
                {
                    "request_id": "r4",
                    "data": [
                        {"id": "event-1", "calendar_id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "updated_at": 1788300000},
                        {"id": "event-2", "calendar_id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "updated_at": 1788310000},
                    ],
                }
            ),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2"]
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert any(
            "Calendar not found or not accessible" in log.log.message for log in output.logs
        ), "expected the skipped 404 calendar to be logged"
        # exactly one events request per calendar: the 404 is not retried
        http_mocker.assert_number_of_calls(subscribed_calendar_request, 1)
        http_mocker.assert_number_of_calls(owned_calendar_request, 1)
