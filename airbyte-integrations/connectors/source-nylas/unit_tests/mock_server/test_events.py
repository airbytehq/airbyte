# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_KEY = "test_api_key"
_URL_BASE = "https://api.us.nylas.com"
_GRANT_ID = "grant-1"
_CONFIG = {
    "api_key": _API_KEY,
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
# Epoch seconds of the configured start_date / end_date, sent as the events time window.
_WINDOW_START = "1788220800"
_WINDOW_END = "1788393600"
_HEADERS = {"Authorization": f"Bearer {_API_KEY}"}


def _grants_request() -> HttpRequest:
    return HttpRequest(url=f"{_URL_BASE}/v3/grants", query_params={"limit": "50"}, headers=_HEADERS)


def _calendars_request() -> HttpRequest:
    return HttpRequest(url=f"{_URL_BASE}/v3/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}, headers=_HEADERS)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}/v3/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _WINDOW_START, "end": _WINDOW_END},
        headers=_HEADERS,
    )


def _data_response(records: list) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req-1", "data": records}), status_code=200)


def _event(event_id: str, calendar_id: str) -> dict:
    return {
        "id": event_id,
        "grant_id": _GRANT_ID,
        "calendar_id": calendar_id,
        "object": "event",
        "title": f"Event {event_id}",
        "updated_at": 1788300000,
    }


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync(self, http_mocker: HttpMocker):
        http_mocker.get(_grants_request(), _data_response([{"id": _GRANT_ID}]))
        http_mocker.get(
            _calendars_request(),
            _data_response([{"id": "cal-primary"}, {"id": "cal-holidays"}, {"id": "cal-work"}]),
        )
        http_mocker.get(_events_request("cal-primary"), _data_response([_event("evt-1", "cal-primary")]))
        # Nylas lists the subscribed holidays calendar but answers 404 when its events are requested.
        holidays_request = _events_request("cal-holidays")
        http_mocker.get(
            holidays_request,
            HttpResponse(
                body='{"request_id": "req-404", "error": {"type": "general", "message": "Not Found"}}',
                status_code=404,
            ),
        )
        http_mocker.get(
            _events_request("cal-work"),
            _data_response([_event("evt-2", "cal-work"), _event("evt-3", "cal-work")]),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert sorted(record.record.data["id"] for record in output.records) == ["evt-1", "evt-2", "evt-3"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The 404 is not retried.
        http_mocker.assert_number_of_calls(holidays_request, 1)
