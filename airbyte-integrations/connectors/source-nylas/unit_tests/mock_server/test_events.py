# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("calendar_a_status", [200, 404])
def test_events_continue_after_empty_or_missing_calendar(calendar_a_status):
    config = {
        "api_key": "test-key",
        "api_server": "us",
        "start_date": "2026-01-01T00:00:00Z",
        "end_date": "2026-01-02T00:00:00Z",
    }
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()

    def request(path, params):
        return HttpRequest(
            url=f"https://api.us.nylas.com/v3/{path}",
            query_params=params,
            headers={"Authorization": "Bearer test-key"},
        )

    with HttpMocker() as http_mocker:
        http_mocker.get(request("grants", {"limit": "50"}), HttpResponse(json.dumps({"data": [{"id": "grant"}]})))
        http_mocker.get(
            request("grants/grant/calendars", {"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": "cal-a"}, {"id": "cal-b"}]})),
        )
        calendar_requests = {}
        for calendar_id in ("cal-a", "cal-b"):
            calendar_requests[calendar_id] = request(
                "grants/grant/events",
                {"limit": "50", "calendar_id": calendar_id, "start": "1767225600", "end": "1767312000"},
            )
        error = {"request_id": "request-a", "error": {"type": "general", "message": "Not Found"}}
        http_mocker.get(
            calendar_requests["cal-a"],
            HttpResponse(json.dumps(error if calendar_a_status == 404 else {"data": []}), calendar_a_status),
        )
        http_mocker.get(
            calendar_requests["cal-b"],
            HttpResponse(json.dumps({"data": [{"id": "event-b", "updated_at": 1767268800}]})),
        )

        output = read(get_source(config), config=config, catalog=catalog, expecting_exception=False)

        http_mocker.assert_number_of_calls(calendar_requests["cal-a"], 1)
        assert [record.record.data["id"] for record in output.records] == ["event-b"]
        assert not output.errors
        assert "INCOMPLETE" not in output.get_stream_statuses("events")
        assert not any(log.log.level == "ERROR" for log in output.logs)
