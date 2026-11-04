# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


BASE_URL = "https://api.us.nylas.com"
START_DATE = "2026-09-01T00:00:00Z"
NOW = "2026-11-04T12:00:00Z"


def epoch(value):
    return str(int(datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()))


@pytest.mark.parametrize("end_date", [None, "2026-09-15T00:00:00Z"])
@pytest.mark.parametrize("response_kind", ["records", "empty", "not_found"])
@freeze_time(NOW)
def test_events_end_date(http_mocker: HttpMocker, end_date, response_kind):
    config = {"api_key": "test-key", "api_server": "us", "start_date": START_DATE}
    if end_date is not None:
        config["end_date"] = end_date
    http_mocker.get(
        HttpRequest(url=f"{BASE_URL}/v3/grants", query_params={"limit": "50"}),
        HttpResponse(body=json.dumps({"data": [{"id": "grant-1"}]})),
    )
    http_mocker.get(
        HttpRequest(url=f"{BASE_URL}/v3/grants/grant-1/calendars", query_params={"limit": "50"}),
        HttpResponse(body=json.dumps({"data": [{"id": "calendar-1"}, {"id": "calendar-2"}]})),
    )
    expected_records = []
    event_requests = []
    for calendar_id in ["calendar-1", "calendar-2"]:
        record = {"id": f"event-{calendar_id}", "updated_at": int(epoch(START_DATE))}
        if response_kind == "records":
            expected_records.append(record)
        request = HttpRequest(
            url=f"{BASE_URL}/v3/grants/grant-1/events",
            query_params={
                "calendar_id": calendar_id,
                "limit": "50",
                "start": epoch(START_DATE),
                "end": epoch(end_date or NOW),
            },
        )
        event_requests.append(request)
        http_mocker.get(
            request,
            HttpResponse(
                body=json.dumps(
                    {"error": {"message": "Not found"}}
                    if response_kind == "not_found"
                    else {"data": [record] if response_kind == "records" else []}
                ),
                status_code=404 if response_kind == "not_found" else 200,
            ),
        )

    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    output = read(get_source(config), config, catalog)

    assert output.errors == [], [error.trace.error.message for error in output.errors]
    assert [message.record.data for message in output.records] == expected_records
    for request in event_requests:
        http_mocker.assert_number_of_calls(request, 1)
