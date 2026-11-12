# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
_PRIMARY_CALENDAR_ID = "primary-calendar"
_HOLIDAYS_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
_CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_START = "1788220800"
_END = "1788393600"


def _response(data, status_code=200):
    return HttpResponse(json.dumps(data), status_code)


def _events_request(calendar_id):
    return HttpRequest(
        url=f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


class TestEvents(TestCase):
    @HttpMocker()
    def test_events_404_for_one_calendar_is_ignored_and_other_calendars_still_sync(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/grants", query_params={"limit": "50"}),
            _response({"data": [{"id": _GRANT_ID}]}),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
            _response({"data": [{"id": _HOLIDAYS_CALENDAR_ID}, {"id": _PRIMARY_CALENDAR_ID}]}),
        )
        holidays_events_request = _events_request(_HOLIDAYS_CALENDAR_ID)
        http_mocker.get(
            holidays_events_request,
            _response({"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}, status_code=404),
        )
        http_mocker.get(
            _events_request(_PRIMARY_CALENDAR_ID),
            _response({"data": [{"id": "event-1", "calendar_id": _PRIMARY_CALENDAR_ID, "updated_at": 1788300000}]}),
        )

        catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == ["event-1"]
        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        http_mocker.assert_number_of_calls(holidays_events_request, 1)
