# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source
from freezegun import freeze_time
from mock_server.request_builder import nylas_request
from mock_server.response_builder import data_response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


@freeze_time("2026-11-05T00:00:00Z")
def test_events_skips_not_found_calendar_and_reads_remaining_calendar():
    http_mocker = HttpMocker()
    config = {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }
    http_mocker.get(
        nylas_request("grants", {"limit": "50"}),
        data_response([{"id": "grant-1"}]),
    )
    http_mocker.get(
        nylas_request("grants/grant-1/calendars", {"limit": "50"}),
        data_response([{"id": "calendar-a"}, {"id": "calendar-b"}]),
    )
    query = {"limit": "50", "start": "1788220800", "end": "1788393600"}
    calendar_a_request = nylas_request("grants/grant-1/events", {**query, "calendar_id": "calendar-a"})
    calendar_b_request = nylas_request("grants/grant-1/events", {**query, "calendar_id": "calendar-b"})
    http_mocker.get(
        calendar_a_request,
        HttpResponse(
            body=json.dumps({"request_id": "test-request", "error": {"type": "general", "message": "Not Found"}}),
            status_code=404,
        ),
    )
    http_mocker.get(
        calendar_b_request,
        data_response(
            [
                {"id": "event-b-1", "calendar_id": "calendar-b", "updated_at": 1788224400},
                {"id": "event-b-2", "calendar_id": "calendar-b", "updated_at": 1788310800},
            ]
        ),
    )

    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    with http_mocker:
        output = read(get_source(config), config=config, catalog=catalog, expecting_exception=False)

    assert not output.errors, "events read must not fail on a calendar 404"
    assert not any(log.log.level == "ERROR" for log in output.logs)
    assert any(log.log.message == "Calendar not found. Skipping this calendar's events." for log in output.logs)
    assert [record.record.data["id"] for record in output.records] == ["event-b-1", "event-b-2"]
    http_mocker.assert_number_of_calls(calendar_a_request, 1)
    http_mocker.assert_number_of_calls(calendar_b_request, 1)
