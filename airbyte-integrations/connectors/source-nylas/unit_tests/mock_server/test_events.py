# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.us.nylas.com"
_GRANT_ID = "grant-1"
_PRIMARY_CALENDAR_ID = "primary-calendar"
_HOLIDAY_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
# 2026-09-01T00:00:00Z and 2026-09-03T00:00:00Z as Unix timestamps.
_START = "1788220800"
_END = "1788393600"

_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}


def _request(path: str, query_params: Optional[Dict[str, Any]] = None) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}{path}", query_params={"limit": "50", **(query_params or {})})


def _response(body: Dict[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _events_request(calendar_id: str) -> HttpRequest:
    return _request(
        f"/v3/grants/{_GRANT_ID}/events",
        {"calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _event(event_id: str, calendar_id: str) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": _GRANT_ID, "calendar_id": calendar_id, "updated_at": 1788300000}


def _read_events(config: Dict[str, Any], expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(config=config), config, catalog, expecting_exception=expecting_exception)


def _mock_grant_and_calendars(http_mocker: HttpMocker, calendar_ids: List[str]) -> None:
    http_mocker.get(_request("/v3/grants"), _response({"data": [{"id": _GRANT_ID}]}))
    http_mocker.get(
        _request(f"/v3/grants/{_GRANT_ID}/calendars"),
        _response({"data": [{"id": calendar_id, "grant_id": _GRANT_ID} for calendar_id in calendar_ids]}),
    )


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_sync(self, http_mocker: HttpMocker) -> None:
        _mock_grant_and_calendars(http_mocker, [_HOLIDAY_CALENDAR_ID, _PRIMARY_CALENDAR_ID])
        http_mocker.get(
            _events_request(_HOLIDAY_CALENDAR_ID),
            _response({"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}, status_code=404),
        )
        http_mocker.get(
            _events_request(_PRIMARY_CALENDAR_ID),
            _response({"request_id": "req-2", "data": [_event("event-1", _PRIMARY_CALENDAR_ID)]}),
        )

        output = _read_events(_CONFIG)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["event-1"]

    @HttpMocker()
    def test_non_404_error_still_fails_the_stream(self, http_mocker: HttpMocker) -> None:
        _mock_grant_and_calendars(http_mocker, [_PRIMARY_CALENDAR_ID])
        http_mocker.get(
            _events_request(_PRIMARY_CALENDAR_ID),
            _response({"request_id": "req-1", "error": {"type": "unauthorized", "message": "Unauthorized"}}, status_code=401),
        )

        output = _read_events(_CONFIG, expecting_exception=True)

        assert output.errors
        assert not output.records
