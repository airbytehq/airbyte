# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
EVENT = {"id": "event_ok", "calendar_id": "cal_ok", "grant_id": "grant_1", "updated_at": 1788307200}


def _response(records: list[dict]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": records}), status_code=200)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}/grants/grant_1/events",
        query_params={"calendar_id": calendar_id, "limit": "50", "start": "1788220800", "end": "1788393600"},
    )


def _mock_parents(http_mocker: HttpMocker, calendars: list[str]) -> None:
    http_mocker.get(HttpRequest(url=f"{BASE_URL}/grants", query_params={"limit": "50"}), _response([{"id": "grant_1"}]))
    http_mocker.get(
        HttpRequest(url=f"{BASE_URL}/grants/grant_1/calendars", query_params={"limit": "50"}),
        _response([{"id": calendar_id, "grant_id": "grant_1"} for calendar_id in calendars]),
    )


def _read():
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(get_source(config=CONFIG), config=CONFIG, catalog=catalog)


class TestEvents(TestCase):
    @HttpMocker()
    def test_skips_inaccessible_calendar_and_reads_accessible_calendar(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker, ["cal_holidays", "cal_ok"])
        http_mocker.get(
            _events_request("cal_holidays"),
            HttpResponse(body=json.dumps({"request_id": "r", "error": {"type": "general", "message": "Not Found"}}), status_code=404),
        )
        http_mocker.get(_events_request("cal_ok"), _response([EVENT]))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event_ok"]

    @HttpMocker()
    def test_reads_accessible_calendar(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker, ["cal_ok"])
        http_mocker.get(_events_request("cal_ok"), _response([EVENT]))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event_ok"]

    @HttpMocker()
    def test_empty_calendar(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker, ["cal_ok"])
        http_mocker.get(_events_request("cal_ok"), _response([]))

        output = _read()

        assert output.errors == []
        assert output.records == []

    @HttpMocker()
    def test_other_errors_still_fail(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker, ["cal_ok"])
        http_mocker.get(
            _events_request("cal_ok"),
            HttpResponse(body=json.dumps({"error": {"type": "general", "message": "Forbidden"}}), status_code=403),
        )

        output = _read()

        assert output.errors
        assert output.records == []
