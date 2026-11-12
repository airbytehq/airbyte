# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

import pytest
from requests_mock import Mocker
from unit_tests.conftest import read_stream

from airbyte_cdk.models import AirbyteStreamStatus, Level, SyncMode


BASE_URL = "https://api.us.nylas.com/v3"
GRANT_ID = "test-grant"
HOLIDAYS = "en.usa#holiday@group.v.calendar.google.com"


def mock_parents(requests_mock: Mocker) -> None:
    requests_mock.get(f"{BASE_URL}/grants?limit=50", json={"data": [{"id": GRANT_ID}]}, complete_qs=True)
    requests_mock.get(
        f"{BASE_URL}/grants/{GRANT_ID}/calendars?limit=50",
        json={"data": [{"id": HOLIDAYS, "read_only": True}, {"id": "primary"}, {"id": "shared", "read_only": True}]},
        complete_qs=True,
    )


def events_url(calendar_id: str, page_token: str | None = None) -> str:
    query = {"limit": 50, "calendar_id": calendar_id, "start": 1788220800, "end": 1788393600}
    if page_token:
        query["page_token"] = page_token
    return f"{BASE_URL}/grants/{GRANT_ID}/events?{urlencode(query)}"


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_events_404_continues_other_calendars(requests_mock: Mocker, config: dict, sync_mode: SyncMode) -> None:
    mock_parents(requests_mock)
    unavailable = requests_mock.get(
        events_url(HOLIDAYS),
        status_code=404,
        json={"request_id": "test-request", "error": {"type": "general", "message": "Not Found"}},
        complete_qs=True,
    )
    for calendar_id, record_id, next_cursor in [("primary", "event-1", "next-page"), ("shared", "event-3", None)]:
        requests_mock.get(
            events_url(calendar_id),
            json={"data": [{"id": record_id, "calendar_id": calendar_id, "updated_at": 1788307200}], "next_cursor": next_cursor},
            complete_qs=True,
        )
    requests_mock.get(
        events_url("primary", "next-page"),
        json={"data": [{"id": "event-2", "calendar_id": "primary", "updated_at": 1788307201}]},
        complete_qs=True,
    )

    output = read_stream(config, sync_mode=sync_mode)

    assert output.errors == [], output.get_formatted_error_message()
    assert sorted(record.record.data["id"] for record in output.records) == ["event-1", "event-2", "event-3"]
    assert unavailable.call_count == 1
    event_requests = [request for request in requests_mock.request_history if request.path.endswith("/events")]
    assert len(event_requests) == 4
    assert not any(log.log.level == Level.ERROR for log in output.logs)
    assert output.is_in_logs("Calendar events are unavailable \\(HTTP 404\\)")
    assert AirbyteStreamStatus.COMPLETE in output.get_stream_statuses("events")
