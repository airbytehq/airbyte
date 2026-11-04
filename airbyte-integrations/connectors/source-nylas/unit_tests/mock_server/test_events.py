# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder


_BASE_URL = "https://api.us.nylas.com"
_START_DATE = "2026-09-01T00:00:00Z"
_END_DATE = "2026-09-03T00:00:00Z"
_EVENTS_ERROR_MESSAGE = (
    "Nylas returned 404 Not Found for this calendar's events (for example, a subscribed calendar whose events "
    "the grant cannot list). Skipping this calendar."
)
_CALENDAR_IDS = ("primary_cal", "holidays_cal")


def _request(path: str, query_params: Dict[str, str]) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}{path}", query_params=query_params)


def _grants_request() -> HttpRequest:
    return _request("/v3/grants", {"limit": "50"})


def _calendars_request() -> HttpRequest:
    return _request("/v3/grants/grant_1/calendars", {"limit": "50"})


def _events_request(calendar_id: str) -> HttpRequest:
    return _request(
        "/v3/grants/grant_1/events",
        {
            "limit": "50",
            "calendar_id": calendar_id,
            "start": "1788220800",
            "end": "1788393600",
        },
    )


def _response(body: Dict[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _event(event_id: str) -> Dict[str, Any]:
    return {"id": event_id, "updated_at": 1788250000}


def _mock_parent_streams(http_mocker: HttpMocker) -> None:
    http_mocker.get(_grants_request(), _response({"data": [{"id": "grant_1"}]}))
    http_mocker.get(_calendars_request(), _response({"data": [{"id": calendar_id} for calendar_id in _CALENDAR_IDS]}))


def _read_events() -> EntrypointOutput:
    config = ConfigBuilder().with_api_key("test_key").with_api_server("us").with_start_date(_START_DATE).with_end_date(_END_DATE).build()
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def _record_ids(output: EntrypointOutput) -> List[str]:
    return [message.record.data["id"] for message in output.records]


class TestEventsErrorHandling(TestCase):
    @HttpMocker()
    def test_events_404_on_one_calendar_skips_it_and_syncs_others(self, http_mocker: HttpMocker) -> None:
        _mock_parent_streams(http_mocker)
        primary_request = _events_request("primary_cal")
        holidays_request = _events_request("holidays_cal")
        http_mocker.get(primary_request, _response({"data": [_event("primary_event")]}))
        http_mocker.get(
            holidays_request,
            _response(
                {"request_id": "request_404", "error": {"type": "general", "message": "Not Found"}},
                status_code=404,
            ),
        )

        output = _read_events()

        assert _record_ids(output) == ["primary_event"]
        assert output.errors == []
        assert any(_EVENTS_ERROR_MESSAGE in message.log.message for message in output.logs)
        http_mocker.assert_number_of_calls(primary_request, 1)
        http_mocker.assert_number_of_calls(holidays_request, 1)

    @HttpMocker()
    def test_events_both_calendars_sync(self, http_mocker: HttpMocker) -> None:
        _mock_parent_streams(http_mocker)
        requests = {calendar_id: _events_request(calendar_id) for calendar_id in _CALENDAR_IDS}
        for calendar_id, request in requests.items():
            http_mocker.get(request, _response({"data": [_event(f"{calendar_id}_event")]}))

        output = _read_events()

        assert output.errors == []
        assert set(_record_ids(output)) == {"primary_cal_event", "holidays_cal_event"}
        for request in requests.values():
            http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_events_403_still_fails(self, http_mocker: HttpMocker) -> None:
        _mock_parent_streams(http_mocker)
        primary_request = _events_request("primary_cal")
        holidays_request = _events_request("holidays_cal")
        http_mocker.get(primary_request, _response({"data": [_event("primary_event")]}))
        http_mocker.get(
            holidays_request,
            _response(
                {"request_id": "request_403", "error": {"type": "general", "message": "Forbidden"}},
                status_code=403,
            ),
        )

        output = _read_events()

        assert output.errors
        http_mocker.assert_number_of_calls(holidays_request, 1)
