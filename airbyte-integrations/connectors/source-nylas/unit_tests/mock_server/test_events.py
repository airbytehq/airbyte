# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone

import pytest
from conftest import get_source

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("event_ids", [["event-1", "event-2"], []])
def test_events_skip_inaccessible_calendar(event_ids):
    config = {
        "api_key": "dummy",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }
    base_url = "https://api.us.nylas.com/v3"
    headers = {"Authorization": "Bearer dummy"}
    start = str(int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp()))
    end = str(int(datetime(2026, 9, 3, tzinfo=timezone.utc).timestamp()))
    good_request = HttpRequest(
        url=f"{base_url}/grants/grant-1/events",
        headers=headers,
        query_params={"limit": "50", "calendar_id": "good-calendar", "start": start, "end": end},
    )
    inaccessible_request = HttpRequest(
        url=f"{base_url}/grants/grant-1/events",
        headers=headers,
        query_params={"limit": "50", "calendar_id": "subscribed-calendar", "start": start, "end": end},
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{base_url}/grants", headers=headers, query_params={"limit": "50"}),
            HttpResponse(body=json.dumps({"data": [{"id": "grant-1"}]}), status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{base_url}/grants/grant-1/calendars", headers=headers, query_params={"limit": "50"}),
            HttpResponse(
                body=json.dumps({"data": [{"id": "subscribed-calendar"}, {"id": "good-calendar"}]}),
                status_code=200,
            ),
        )
        http_mocker.get(
            inaccessible_request,
            HttpResponse(
                body=json.dumps({"request_id": "request-404", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        http_mocker.get(
            good_request,
            HttpResponse(
                body=json.dumps({"data": [{"id": event_id, "updated_at": int(start) + 60} for event_id in event_ids]}),
                status_code=200,
            ),
        )
        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
        )
        http_mocker.assert_number_of_calls(inaccessible_request, 1)
        http_mocker.assert_number_of_calls(good_request, 1)

    assert len(output.records) == len(event_ids)
    assert {message.record.data["id"] for message in output.records} == set(event_ids)
    assert not [message for message in output.logs if message.log.level == Level.ERROR]
    assert not output.errors
