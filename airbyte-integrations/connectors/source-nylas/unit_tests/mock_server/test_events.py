# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-api-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
GRANT_ID = "test-grant"


def given_calendars(http_mocker: HttpMocker, calendar_ids: list[str]) -> None:
    http_mocker.get(
        HttpRequest(url=f"{BASE_URL}/grants", query_params={"limit": "50"}),
        HttpResponse(body=json.dumps({"data": [{"id": GRANT_ID, "provider": "google"}]})),
    )
    http_mocker.get(
        HttpRequest(url=f"{BASE_URL}/grants/{GRANT_ID}/calendars", query_params={"limit": "50"}),
        HttpResponse(body=json.dumps({"data": [{"id": calendar_id} for calendar_id in calendar_ids]})),
    )


def events_request(calendar_id: str, page_token: str | None = None) -> HttpRequest:
    params = {
        "calendar_id": calendar_id,
        "limit": "50",
        "start": "1788220800",
        "end": "1788393600",
    }
    if page_token:
        params["page_token"] = page_token
    return HttpRequest(url=f"{BASE_URL}/grants/{GRANT_ID}/events", query_params=params)


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_events_continue_after_calendar_not_found(sync_mode: SyncMode) -> None:
    with HttpMocker() as http_mocker:
        given_calendars(http_mocker, ["holidays", "primary", "shared"])
        missing_calendar = events_request("holidays")
        http_mocker.get(
            missing_calendar,
            HttpResponse(
                body=json.dumps({"request_id": "test-request", "error": {"type": "general", "message": "Not Found"}}),
                status_code=404,
            ),
        )
        for calendar_id, event_ids in [("primary", ["event-1", "event-2"]), ("shared", ["event-3"])]:
            for index, event_id in enumerate(event_ids):
                response = {"data": [{"id": event_id, "updated_at": 1788307200, "calendar_id": calendar_id}]}
                if index == 0 and len(event_ids) > 1:
                    response["next_cursor"] = "next-page"
                http_mocker.get(
                    events_request(calendar_id, "next-page" if index else None),
                    HttpResponse(body=json.dumps(response)),
                )

        output = read(get_source(CONFIG), CONFIG, CatalogBuilder().with_stream("events", sync_mode).build())

        assert output.errors == []
        assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2", "event-3"]
        assert not any(log.log.level == "ERROR" for log in output.logs)
        http_mocker.assert_number_of_calls(missing_calendar, 1)


@pytest.mark.parametrize(
    "endpoint,status_code,failure_type,message",
    [
        (
            "events",
            401,
            FailureType.config_error,
            "HTTP Status Code: 401. Error: Unauthorized. Please ensure you are authenticated correctly.",
        ),
        (
            "events",
            403,
            FailureType.config_error,
            "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource.",
        ),
        (
            "calendars",
            404,
            FailureType.system_error,
            "HTTP Status Code: 404. Error: Not found. The requested resource was not found on the server.",
        ),
        (
            "grants",
            404,
            FailureType.system_error,
            "HTTP Status Code: 404. Error: Not found. The requested resource was not found on the server.",
        ),
    ],
)
def test_errors_outside_events_not_found_still_fail(endpoint: str, status_code: int, failure_type: FailureType, message: str) -> None:
    with HttpMocker() as http_mocker:
        if endpoint == "events":
            given_calendars(http_mocker, ["primary"])
            failed_request = events_request("primary")
        else:
            if endpoint == "calendars":
                http_mocker.get(
                    HttpRequest(url=f"{BASE_URL}/grants", query_params={"limit": "50"}),
                    HttpResponse(body=json.dumps({"data": [{"id": GRANT_ID}]})),
                )
            path = "grants" if endpoint == "grants" else f"grants/{GRANT_ID}/calendars"
            failed_request = HttpRequest(url=f"{BASE_URL}/{path}", query_params={"limit": "50"})
        http_mocker.get(
            failed_request,
            HttpResponse(body=json.dumps({"error": {"type": "general", "message": "Request failed"}}), status_code=status_code),
        )

        output = read(
            get_source(CONFIG),
            CONFIG,
            CatalogBuilder().with_stream("events", SyncMode.full_refresh).build(),
            expecting_exception=True,
        )

        assert output.records == []
        assert any(error.trace.error.failure_type == failure_type and error.trace.error.message == message for error in output.errors)
        http_mocker.assert_number_of_calls(failed_request, 1)


@pytest.mark.parametrize("status_code", [429, 500])
def test_events_retry_transient_errors(status_code: int) -> None:
    with HttpMocker() as http_mocker, patch("time.sleep"):
        given_calendars(http_mocker, ["primary"])
        request = events_request("primary")
        http_mocker.get(
            request,
            [
                HttpResponse(body=json.dumps({"error": {"type": "general", "message": "Try again"}}), status_code=status_code),
                HttpResponse(body=json.dumps({"data": [{"id": "event-1", "updated_at": 1788307200}]})),
            ],
        )

        output = read(get_source(CONFIG), CONFIG, CatalogBuilder().with_stream("events", SyncMode.full_refresh).build())

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["event-1"]
        http_mocker.assert_number_of_calls(request, 2)
