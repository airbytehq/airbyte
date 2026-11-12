# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_events_skips_calendar_not_found() -> None:
    config = {
        "api_key": "test_api_key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }
    base_url = "https://api.us.nylas.com/v3/grants"
    event_params = {"limit": "50", "start": "1788220800", "end": "1788393600"}
    holidays_request = HttpRequest(
        url=f"{base_url}/grant_1/events", query_params={**event_params, "calendar_id": "cal_holidays"}
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=base_url, query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "grant_1"}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{base_url}/grant_1/calendars", query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "cal_ok"}, {"id": "cal_holidays"}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{base_url}/grant_1/events", query_params={**event_params, "calendar_id": "cal_ok"}),
            HttpResponse(body=json.dumps({"data": [{"id": "event_ok", "updated_at": 1788307200}]})),
        )
        http_mocker.get(
            holidays_request,
            HttpResponse(status_code=404, body=json.dumps({"error": {"type": "general", "message": "Not Found"}})),
        )
        output = read(
            get_source(config),
            config,
            CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
        )

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["event_ok"]
        http_mocker.assert_number_of_calls(holidays_request, 1)
