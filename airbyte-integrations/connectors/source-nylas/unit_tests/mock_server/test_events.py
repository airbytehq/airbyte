# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def response(body, status_code=200):
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def request(path, **query_params):
    return HttpRequest(
        url=f"https://api.us.nylas.com/v3/{path}",
        headers={"Authorization": "Bearer test-api-key"},
        query_params=query_params,
    )


@HttpMocker()
def test_events_skips_inaccessible_calendar(http_mocker=None):
    config = {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-01-02T00:00:00Z",
    }
    http_mocker.get(request("grants", limit="50"), response({"data": [{"id": "grant-1"}]}))
    http_mocker.get(
        request("grants/grant-1/calendars", limit="50"),
        response({"data": [{"id": "calendar-a"}, {"id": "calendar-b"}]}),
    )
    events_requests = {
        calendar_id: request("grants/grant-1/events", calendar_id=calendar_id, limit="50", start="1704067200", end="1704153600")
        for calendar_id in ("calendar-a", "calendar-b")
    }
    http_mocker.get(
        events_requests["calendar-a"],
        response({"request_id": "request-1", "error": {"type": "general", "message": "Not Found"}}, 404),
    )
    http_mocker.get(
        events_requests["calendar-b"],
        response({"data": [{"id": "event-b1", "updated_at": 1704100000}, {"id": "event-b2", "updated_at": 1704100001}]}),
    )

    output = read(
        get_source(config),
        config=config,
        catalog=CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
    )

    assert not output.errors
    assert sorted(record.record.data["id"] for record in output.records) == ["event-b1", "event-b2"]
    assert not any(log.log.level == Level.ERROR for log in output.logs)
    assert any(
        log.log.message == "The calendar identified by calendar_id is not accessible; skipped events for this calendar (HTTP 404)."
        for log in output.logs
    )
    for events_request in events_requests.values():
        http_mocker.assert_number_of_calls(events_request, 1)
