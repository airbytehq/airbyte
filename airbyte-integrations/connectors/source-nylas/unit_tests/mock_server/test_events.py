# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder


_BASE_URL = "https://api.us.nylas.com/v3"
_GRANT_ID = "grant-1"
# 2026-09-01T00:00:00Z and 2026-09-03T00:00:00Z as epoch seconds (the config's start/end dates).
_START = "1788220800"
_END = "1788393600"


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"request_id": "req", "data": records}), 200)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END},
    )


def _given_grant_with_calendars(http_mocker: HttpMocker, calendar_ids: List[str]) -> None:
    http_mocker.get(HttpRequest(url=f"{_BASE_URL}/grants", query_params={"limit": "50"}), _page([{"id": _GRANT_ID}]))
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _page([{"id": calendar_id, "grant_id": _GRANT_ID} for calendar_id in calendar_ids]),
    )


class TestEvents(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_still_sync(self, http_mocker: HttpMocker) -> None:
        """A subscribed calendar (e.g. a Google holidays calendar) can be listed by /calendars but return
        404 from /events. That calendar must be skipped without failing the stream, and events from the
        grant's other calendars must still be emitted."""
        _given_grant_with_calendars(http_mocker, ["primary-cal", "holidays-cal", "work-cal"])
        http_mocker.get(
            _events_request("primary-cal"),
            _page([{"id": "evt-1", "calendar_id": "primary-cal", "updated_at": 1788300000}]),
        )
        http_mocker.get(
            _events_request("holidays-cal"),
            HttpResponse(json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}), 404),
        )
        http_mocker.get(
            _events_request("work-cal"),
            _page([{"id": "evt-2", "calendar_id": "work-cal", "updated_at": 1788310000}]),
        )

        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

        assert sorted(record.record.data["id"] for record in output.records) == ["evt-1", "evt-2"]
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
