# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_events_skips_missing_calendar_and_reads_remaining_calendar():
    config = {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    base_url = "https://api.us.nylas.com/v3/grants"
    missing_calendar_request = HttpRequest(
        url=f"{base_url}/grant-1/events",
        query_params={"limit": "50", "calendar_id": "cal-a", "start": "1788220800", "end": "1788393600"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=base_url, query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "grant-1"}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{base_url}/grant-1/calendars", query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "cal-a"}, {"id": "cal-b"}]})),
        )
        http_mocker.get(
            missing_calendar_request,
            HttpResponse(
                body=json.dumps({"request_id": "request-1", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(
            HttpRequest(
                url=f"{base_url}/grant-1/events",
                query_params={"limit": "50", "calendar_id": "cal-b", "start": "1788220800", "end": "1788393600"},
            ),
            HttpResponse(body=json.dumps({"data": [{"id": "event-b", "updated_at": 1788307200}]})),
        )

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["event-b"]
        http_mocker.assert_number_of_calls(missing_calendar_request, 1)
