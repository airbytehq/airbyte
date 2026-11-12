# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "api_server": "us",
    "api_key": "test-api-key",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
_BASE_URL = "https://api.us.nylas.com/v3/grants"


@pytest.mark.parametrize("normal_events", [[{"id": "event-a", "updated_at": 1788307200}], []])
@pytest.mark.parametrize("holiday_status", [200, 404])
def test_events_read_skips_inaccessible_calendar(normal_events, holiday_status):
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=_BASE_URL, query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "grant-a"}]}), status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE_URL}/grant-a/calendars", query_params={"limit": "50"}),
            HttpResponse(
                body=json.dumps({"data": [{"id": "calendar-a", "name": "Primary"}, {"id": "holidays", "read_only": True}]}),
                status_code=200,
            ),
        )
        requests = []
        for calendar_id, events in [("calendar-a", normal_events), ("holidays", [])]:
            request = HttpRequest(
                url=f"{_BASE_URL}/grant-a/events",
                query_params={"limit": "50", "calendar_id": calendar_id, "start": "1788220800", "end": "1788393600"},
            )
            status = holiday_status if calendar_id == "holidays" else 200
            body = {"request_id": "x", "error": {"type": "general", "message": "Not Found"}} if status == 404 else {"data": events}
            http_mocker.get(request, HttpResponse(body=json.dumps(body), status_code=status))
            requests.append(request)

        catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog, expecting_exception=True)

        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    assert [record.record.data["id"] for record in output.records] == [event["id"] for event in normal_events]
    assert not output.errors
    assert not any(log.log.level == "ERROR" for log in output.logs)
