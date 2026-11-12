# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from conftest import get_source


_API = "https://api.us.nylas.com"
_GRANT_ID = "grant-1"
_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_START = "1788220800"  # 2026-09-01T00:00:00Z
_END = "1788393600"  # 2026-09-03T00:00:00Z
_HEADERS = {"Authorization": "Bearer test-api-key"}


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_API}/v3/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
        headers=_HEADERS,
    )


def _data(records: list) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req-1", "data": records}), status_code=200)


def _event(event_id: str, calendar_id: str) -> dict:
    return {"id": event_id, "calendar_id": calendar_id, "grant_id": _GRANT_ID, "updated_at": 1788300000}


def _read_events():
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog, expecting_exception=False)


def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync():
    """Nylas answers 404 on /events for some calendars it lists (e.g. subscribed holiday calendars)."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{_API}/v3/grants", query_params={"limit": "50"}, headers=_HEADERS),
            _data([{"id": _GRANT_ID, "provider": "google"}]),
        )
        http_mocker.get(
            HttpRequest(url=f"{_API}/v3/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}, headers=_HEADERS),
            _data([{"id": "primary-cal"}, {"id": "holiday-cal"}, {"id": "team-cal"}]),
        )
        http_mocker.get(_events_request("primary-cal"), _data([_event("evt-1", "primary-cal")]))
        holiday_request = _events_request("holiday-cal")
        http_mocker.get(
            holiday_request,
            HttpResponse(
                body=json.dumps({"request_id": "req-2", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(_events_request("team-cal"), _data([_event("evt-2", "team-cal"), _event("evt-3", "team-cal")]))

        output = _read_events()

        assert sorted(record.record.data["id"] for record in output.records) == ["evt-1", "evt-2", "evt-3"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The 404 is not retried: the holiday calendar is requested exactly once.
        http_mocker.assert_number_of_calls(holiday_request, 1)
