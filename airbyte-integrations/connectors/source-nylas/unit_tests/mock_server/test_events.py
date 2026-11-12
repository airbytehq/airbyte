# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_URL_BASE = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_PRIMARY_CALENDAR_ID = "primary-calendar"
_SUBSCRIBED_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
# start_date / end_date below, as the epoch seconds sent in the `start` / `end` query params.
_WINDOW_START = "1788220800"
_WINDOW_END = "1788393600"

_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": records}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _WINDOW_START, "end": _WINDOW_END},
    )


def _given_grant_with_primary_and_subscribed_calendar(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/grants", query_params={"limit": "50"}),
        _page([{"id": _GRANT_ID, "provider": "google"}]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _page(
            [
                {"id": _SUBSCRIBED_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": False, "read_only": True},
                {"id": _PRIMARY_CALENDAR_ID, "grant_id": _GRANT_ID, "is_owned_by_user": True, "is_primary": True},
            ]
        ),
    )


class TestEvents(TestCase):
    @HttpMocker()
    def test_404_for_subscribed_calendar_is_skipped_and_other_calendars_still_sync(self, http_mocker: HttpMocker) -> None:
        """Nylas answers 404 on /events for some subscribed (e.g. public holiday) calendars that /calendars lists.

        That calendar's partition must be skipped without failing the stream, so events from the
        grant's other calendars are still emitted.
        """
        _given_grant_with_primary_and_subscribed_calendar(http_mocker)
        subscribed_calendar_events_request = _events_request(_SUBSCRIBED_CALENDAR_ID)
        http_mocker.get(
            subscribed_calendar_events_request,
            HttpResponse(
                body=json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(
            _events_request(_PRIMARY_CALENDAR_ID),
            _page(
                [
                    {"id": "event-1", "calendar_id": _PRIMARY_CALENDAR_ID, "grant_id": _GRANT_ID, "updated_at": 1788300000},
                    {"id": "event-2", "calendar_id": _PRIMARY_CALENDAR_ID, "grant_id": _GRANT_ID, "updated_at": 1788310000},
                ]
            ),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == ["event-1", "event-2"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The 404 is requested exactly once (not retried) per sync.
        http_mocker.assert_number_of_calls(subscribed_calendar_events_request, 1)
