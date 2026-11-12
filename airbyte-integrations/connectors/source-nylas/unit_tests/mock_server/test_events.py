# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3/grants"


def response(data, status_code=200):
    return HttpResponse(body=json.dumps(data), status_code=status_code)


@pytest.mark.parametrize("event_ids", [["event_1", "event_2"], []])
def test_events_skips_inaccessible_calendar(http_mocker: HttpMocker, event_ids):
    http_mocker.get(
        HttpRequest(BASE_URL, query_params={"limit": "50"}),
        response({"data": [{"id": "grant_1"}]}),
    )
    http_mocker.get(
        HttpRequest(f"{BASE_URL}/grant_1/calendars", query_params={"limit": "50"}),
        response({"data": [{"id": "cal_subscribed"}, {"id": "cal_ok"}]}),
    )
    time_params = {
        "start": str(int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp())),
        "end": str(int(datetime(2026, 9, 3, tzinfo=timezone.utc).timestamp())),
        "limit": "50",
    }
    subscribed_request = HttpRequest(
        f"{BASE_URL}/grant_1/events", query_params={**time_params, "calendar_id": "cal_subscribed"}
    )
    ok_request = HttpRequest(f"{BASE_URL}/grant_1/events", query_params={**time_params, "calendar_id": "cal_ok"})
    http_mocker.get(subscribed_request, response({"error": {"type": "general", "message": "Not Found"}}, 404))
    http_mocker.get(
        ok_request,
        response({"data": [{"id": event_id, "updated_at": int(time_params["start"])} for event_id in event_ids]}),
    )

    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    output = read(get_source(CONFIG), config=CONFIG, catalog=catalog, expecting_exception=True)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == event_ids
    http_mocker.assert_number_of_calls(ok_request, 1)
    http_mocker.assert_number_of_calls(subscribed_request, 1)


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker
