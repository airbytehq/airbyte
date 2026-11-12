# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from unit_tests.conftest import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder


_STREAM_NAME = "events"
_GRANT_ID = "grant_1"
# start_date / end_date from ConfigBuilder as unix seconds
_START = "1788220800"
_END = "1788393600"


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req", "data": records}), status_code=200)


def _events_request(calendar_id: str):
    return (
        NylasRequestBuilder.events_endpoint(_GRANT_ID)
        .with_limit()
        .with_query_param("calendar_id", calendar_id)
        .with_query_param("start", _START)
        .with_query_param("end", _END)
        .build()
    )


def _event(event_id: str, calendar_id: str) -> Dict[str, Any]:
    return {
        "id": event_id,
        "grant_id": _GRANT_ID,
        "calendar_id": calendar_id,
        "updated_at": 1788300000,
        "title": event_id,
    }


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_calendar_returning_404_is_skipped_and_other_calendars_sync(self, http_mocker: HttpMocker) -> None:
        """A 404 on one calendar (e.g. a subscribed holidays calendar) must not fail the stream."""
        http_mocker.get(
            NylasRequestBuilder.grants_endpoint().with_limit().build(),
            _page([{"id": _GRANT_ID, "provider": "google"}]),
        )
        http_mocker.get(
            NylasRequestBuilder.calendars_endpoint(_GRANT_ID).with_limit().build(),
            _page(
                [
                    {"id": "cal_primary", "grant_id": _GRANT_ID, "is_owned_by_user": True},
                    {"id": "cal_holidays", "grant_id": _GRANT_ID, "is_owned_by_user": False},
                    {"id": "cal_work", "grant_id": _GRANT_ID, "is_owned_by_user": True},
                ]
            ),
        )
        http_mocker.get(_events_request("cal_primary"), _page([_event("evt_primary", "cal_primary")]))
        http_mocker.get(
            _events_request("cal_holidays"),
            HttpResponse(
                body=json.dumps({"request_id": "req", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(_events_request("cal_work"), _page([_event("evt_work", "cal_work")]))

        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(get_source(config=config), config, catalog)

        assert sorted(record.record.data["id"] for record in output.records) == ["evt_primary", "evt_work"]
        assert not output.errors
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert any("calendar was not found" in log.log.message for log in output.logs)
