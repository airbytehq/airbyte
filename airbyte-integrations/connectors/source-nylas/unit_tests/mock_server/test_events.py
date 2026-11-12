# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder
from mock_server.response_builder import records_response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import get_source


@pytest.mark.parametrize("subscribed_first", [True, False], ids=["subscribed-first", "subscribed-last"])
@pytest.mark.parametrize("event_ids", [("event-1", "event-2"), ()], ids=["records", "empty"])
def test_read_skips_inaccessible_calendar_events(subscribed_first, event_ids):
    calendars = [
        {"id": "normal-calendar", "grant_id": "grant-1", "read_only": False},
        {"id": "subscribed-calendar", "grant_id": "grant-1", "read_only": True},
    ]
    if subscribed_first:
        calendars.reverse()
    requests = {
        calendar["id"]: (
            NylasRequestBuilder.endpoint("/grants/grant-1/events")
            .with_query_param("calendar_id", calendar["id"])
            .with_query_param("start", "1704067200")
            .with_query_param("end", "1704153600")
            .build()
        )
        for calendar in calendars
    }
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(NylasRequestBuilder.endpoint("/grants").build(), records_response([{"id": "grant-1"}]))
        http_mocker.get(NylasRequestBuilder.endpoint("/grants/grant-1/calendars").build(), records_response(calendars))
        http_mocker.get(
            requests["normal-calendar"],
            records_response([{"id": event_id, "calendar_id": "normal-calendar", "updated_at": 1704110400} for event_id in event_ids]),
        )
        http_mocker.get(
            requests["subscribed-calendar"],
            HttpResponse(
                body=json.dumps({"request_id": "test-request", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        assert len(output.records) == len(event_ids)
        assert {record.record.data["id"] for record in output.records} == set(event_ids)
        for request in requests.values():
            http_mocker.assert_number_of_calls(request, 1)
