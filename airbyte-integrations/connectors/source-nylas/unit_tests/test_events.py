# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.us.nylas.com"
_START = 1790812800  # 2026-10-01T00:00:00Z
_END = 1791072000  # 2026-10-04T00:00:00Z


def _request(path, **params):
    return HttpRequest(url=f"{_BASE_URL}/v3/{path}", query_params={"limit": "50", **params})


def _page(records):
    return HttpResponse(body=json.dumps({"data": records}), status_code=200)


@freeze_time("2026-10-04T00:00:00Z")
@pytest.mark.parametrize("end_date", ["2026-10-03T00:00:00Z", None, ""])
@pytest.mark.parametrize("response_kind", ["records", "empty", "not_found"])
def test_events_use_update_bounds_for_each_calendar(end_date, response_kind):
    config = {"api_key": "test-token", "api_server": "us", "start_date": "2026-10-01T00:00:00Z"}
    if end_date is not None:
        config["end_date"] = end_date
    end = 1790985600 if end_date else _END
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()

    with HttpMocker() as http_mocker:
        grants = _request("grants")
        calendars = _request("grants/grant-1/calendars")
        http_mocker.get(grants, _page([{"id": "grant-1"}]))
        http_mocker.get(calendars, _page([{"id": "calendar-1"}, {"id": "calendar-2"}]))
        requests = []
        for calendar_id in ["calendar-1", "calendar-2"]:
            request = _request(
                "grants/grant-1/events",
                calendar_id=calendar_id,
                updated_after=str(_START),
                updated_before=str(end),
            )
            requests.append(request)
            event = {
                "id": f"event-{calendar_id}",
                "updated_at": _START + 3600,
                "when": {"start_time": 1893456000, "end_time": 1893459600},
            }
            response = _page([event] if response_kind == "records" else [])
            if response_kind == "not_found":
                response = HttpResponse(body=json.dumps({"error": {"message": "Calendar not found"}}), status_code=404)
            http_mocker.get(request, response)

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == (
            ["event-calendar-1", "event-calendar-2"] if response_kind == "records" else []
        )
        http_mocker.assert_number_of_calls(grants, 2)
        http_mocker.assert_number_of_calls(calendars, 1)
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)
