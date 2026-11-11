# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


BASE_URL = "https://api.us.nylas.com/v3"
START = 1788220800
END = 1788393600


def mock_parents(http_mocker: Mocker) -> None:
    http_mocker.get(
        f"{BASE_URL}/grants?limit=50",
        json={"data": [{"id": "grant-1", "provider": "google"}]},
        complete_qs=True,
    )
    http_mocker.get(
        f"{BASE_URL}/grants/grant-1/calendars?limit=50",
        json={
            "data": [
                {"id": "holidays", "grant_id": "grant-1", "read_only": True},
                {"id": "primary", "grant_id": "grant-1", "read_only": True},
            ]
        },
        complete_qs=True,
    )


def events_url(calendar_id: str, page_token: str | None = None) -> str:
    url = f"{BASE_URL}/grants/grant-1/events?limit=50&calendar_id={calendar_id}&start={START}&end={END}"
    return f"{url}&page_token={page_token}" if page_token else url


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_calendar_404_does_not_abort_other_calendars(config: dict, requests_mock: Mocker, sync_mode: SyncMode) -> None:
    mock_parents(requests_mock)
    unavailable = requests_mock.get(
        events_url("holidays"),
        status_code=404,
        json={"request_id": "test-request", "error": {"type": "general", "message": "Not Found"}},
        complete_qs=True,
    )
    first_page = requests_mock.get(
        events_url("primary"),
        json={
            "data": [{"id": "event-1", "grant_id": "grant-1", "calendar_id": "primary", "updated_at": START + 1}],
            "next_cursor": "page-2",
        },
        complete_qs=True,
    )
    second_page = requests_mock.get(
        events_url("primary", "page-2"),
        json={"data": [{"id": "event-2", "grant_id": "grant-1", "calendar_id": "primary", "updated_at": START + 2}]},
        complete_qs=True,
    )
    catalog = CatalogBuilder().with_stream("events", sync_mode).build()
    output = read(get_source(config, catalog), config, catalog)

    assert not output.errors
    assert {record.record.data["id"] for record in output.records} == {"event-1", "event-2"}
    assert len(output.records) == 2
    assert unavailable.call_count == first_page.call_count == second_page.call_count == 1
    assert any(
        log.log.message == "Calendar events are unavailable (HTTP 404). Skipping this calendar and continuing with the remaining calendars."
        for log in output.logs
    )
    assert not any(log.log.level == "ERROR" for log in output.logs)
