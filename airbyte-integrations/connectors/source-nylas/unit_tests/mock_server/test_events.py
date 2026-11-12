# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test_api_key"
_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_OWNED_CALENDAR_ID = "owned-calendar"
_SUBSCRIBED_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
# 2026-09-01T00:00:00Z and 2026-09-03T00:00:00Z, as sent in the failing request from the issue
_START = "1788220800"
_END = "1788393600"
_CONFIG = {
    "api_key": _API_KEY,
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_NOT_FOUND_BODY = {"request_id": "req-404", "error": {"type": "general", "message": "Not Found"}}


def _request(path: str, query_params: Dict[str, str]) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}{path}", query_params=query_params, headers={"Authorization": f"Bearer {_API_KEY}"})


def _response(body: Dict[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return _response({"request_id": "req", "data": records})


def _events_request(calendar_id: str) -> HttpRequest:
    return _request(
        f"/grants/{_GRANT_ID}/events",
        {"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _given_grant_with_owned_and_subscribed_calendars(http_mocker: HttpMocker) -> None:
    http_mocker.get(_request("/grants", {"limit": "50"}), _page([{"id": _GRANT_ID}]))
    http_mocker.get(
        _request(f"/grants/{_GRANT_ID}/calendars", {"limit": "50"}),
        _page(
            [
                {"id": _SUBSCRIBED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": False, "read_only": True},
                {"id": _OWNED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": True, "read_only": False},
            ]
        ),
    )


def _read_events(sync_mode: SyncMode):
    catalog = CatalogBuilder().with_stream("events", sync_mode).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog)


class TestEvents(TestCase):
    @HttpMocker()
    def test_404_for_one_calendar_is_skipped_and_other_calendars_still_sync(self, http_mocker: HttpMocker) -> None:
        """
        Nylas answers 404 'Not Found' on /events for some subscribed calendars (e.g. a Google public holidays
        calendar) even though /calendars lists them. That calendar must be skipped with a log message instead of
        failing the whole events stream, so events from the grant's other calendars are still emitted.
        """
        _given_grant_with_owned_and_subscribed_calendars(http_mocker)
        subscribed_calendar_events_request = _events_request(_SUBSCRIBED_CALENDAR_ID)
        http_mocker.get(subscribed_calendar_events_request, _response(_NOT_FOUND_BODY, status_code=404))
        http_mocker.get(
            _events_request(_OWNED_CALENDAR_ID),
            _page(
                [
                    {"id": "event-1", "calendar_id": _OWNED_CALENDAR_ID, "updated_at": 1788300000},
                    {"id": "event-2", "calendar_id": _OWNED_CALENDAR_ID, "updated_at": 1788310000},
                ]
            ),
        )

        output = _read_events(SyncMode.full_refresh)

        assert [record.record.data["id"] for record in output.records] == ["event-1", "event-2"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert any(
            "Skipping events for this calendar because Nylas returned 404 Not Found" in log.log.message
            and f"(request: {_BASE_URL}/grants/{_GRANT_ID}/events)" in log.log.message
            for log in output.logs
        )
        http_mocker.assert_number_of_calls(subscribed_calendar_events_request, 1)
