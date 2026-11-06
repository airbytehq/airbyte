# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

import pytest
from conftest import get_source
from requests_mock import Mocker

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_BASE_URL = "https://api.us.nylas.com/v3/grants"
_START = "1788220800"
_END = "1788393600"


def events_url(calendar_id: str, page_token: str = "") -> str:
    params = {"limit": "50", "calendar_id": calendar_id, "start": _START, "end": _END}
    if page_token:
        params["page_token"] = page_token
    return f"{_BASE_URL}/grant-1/events?{urlencode(params)}"


def event(event_id: str, calendar_id: str) -> dict:
    return {"id": event_id, "calendar_id": calendar_id, "grant_id": "grant-1", "updated_at": 1788307200}


@pytest.mark.parametrize("error_type", ["general", "api.not_found_error"])
@pytest.mark.parametrize("missing_page", ["", "next-page"])
def test_events_404_skips_calendar_and_reads_remaining_calendars(
    config: dict[str, str], requests_mock: Mocker, error_type: str, missing_page: str
) -> None:
    requests_mock.get(f"{_BASE_URL}?limit=50", json={"data": [{"id": "grant-1"}]}, complete_qs=True)
    requests_mock.get(
        f"{_BASE_URL}/grant-1/calendars?limit=50",
        json={"data": [{"id": "primary"}, {"id": "holidays", "read_only": True}, {"id": "shared", "read_only": True}]},
        complete_qs=True,
    )
    requests_mock.get(
        events_url("primary"),
        json={"data": [event("event-1", "primary")], "next_cursor": "next-page"},
        complete_qs=True,
    )
    requests_mock.get(
        events_url("primary", "next-page"),
        json={"data": [event("event-2", "primary")]},
        complete_qs=True,
    )
    if missing_page:
        requests_mock.get(
            events_url("holidays"),
            json={"data": [event("holiday-event", "holidays")], "next_cursor": missing_page},
            complete_qs=True,
        )
    missing_calendar = requests_mock.get(
        events_url("holidays", missing_page),
        status_code=404,
        json={"request_id": "test-request", "error": {"type": error_type, "message": "Not Found"}},
        complete_qs=True,
    )
    requests_mock.get(events_url("shared"), json={"data": [event("event-3", "shared")]}, complete_qs=True)

    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    output = read(get_source(config), config=config, catalog=catalog)

    assert not output.errors
    expected_ids = ["event-1", "event-2", "event-3"] + (["holiday-event"] if missing_page else [])
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids
    assert missing_calendar.call_count == 1
    assert not any(log.log.level == Level.ERROR for log in output.logs)
    assert any("404" in log.log.message and "calendar" in log.log.message for log in output.logs)
    assert output.get_stream_statuses("events")[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize("status", [401, 403])
def test_events_other_client_errors_remain_fatal(config: dict[str, str], requests_mock: Mocker, status: int) -> None:
    requests_mock.get(f"{_BASE_URL}?limit=50", json={"data": [{"id": "grant-1"}]}, complete_qs=True)
    requests_mock.get(f"{_BASE_URL}/grant-1/calendars?limit=50", json={"data": [{"id": "primary"}]}, complete_qs=True)
    failed_request = requests_mock.get(
        events_url("primary"),
        status_code=status,
        json={"error": {"type": "grant.access_denied", "message": "Access denied"}},
        complete_qs=True,
    )

    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    output = read(get_source(config), config=config, catalog=catalog, expecting_exception=True)

    assert output.records == []
    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert any(f"HTTP Status Code: {status}" in error.trace.error.message for error in output.errors)
    assert failed_request.call_count == 1


def test_events_parent_calendar_404_remains_fatal(config: dict[str, str], requests_mock: Mocker) -> None:
    requests_mock.get(f"{_BASE_URL}?limit=50", json={"data": [{"id": "grant-1"}]}, complete_qs=True)
    failed_request = requests_mock.get(
        f"{_BASE_URL}/grant-1/calendars?limit=50",
        status_code=404,
        json={"error": {"type": "grant.not_found", "message": "Not Found"}},
        complete_qs=True,
    )

    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    output = read(get_source(config), config=config, catalog=catalog, expecting_exception=True)

    assert output.records == []
    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.system_error
    assert any("HTTP Status Code: 404" in error.trace.error.message for error in output.errors)
    assert failed_request.call_count == 1
