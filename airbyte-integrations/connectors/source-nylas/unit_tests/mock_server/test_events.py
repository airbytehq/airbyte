# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog, Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


sys.path.append(str(Path(__file__).parent.parent))
from conftest import get_source  # noqa: E402


STREAM = "events"
BASE = "https://api.us.nylas.com/v3"
GRANT = "grant-1"
CONFIG = {
    "api_key": "test-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
# start_date / end_date as epoch seconds, matching the request in the reported failure.
WINDOW = {"start": "1788220800", "end": "1788393600"}
CALENDARS = ["primary-cal", "holidays-cal", "team-cal"]


def _page(records: list) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "r", "data": records}), status_code=200)


def _event(event_id: str, calendar_id: str) -> dict:
    return {"id": event_id, "grant_id": GRANT, "calendar_id": calendar_id, "updated_at": 1788300000, "object": "event"}


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(STREAM, sync_mode).build()


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_events_skips_calendar_returning_404_and_syncs_other_calendars(sync_mode: SyncMode) -> None:
    with HttpMocker() as http:
        http.get(HttpRequest(f"{BASE}/grants", query_params={"limit": "50"}), _page([{"id": GRANT}]))
        http.get(
            HttpRequest(f"{BASE}/grants/{GRANT}/calendars", query_params={"limit": "50"}),
            _page([{"id": calendar_id, "grant_id": GRANT} for calendar_id in CALENDARS]),
        )
        event_requests = {
            calendar_id: HttpRequest(f"{BASE}/grants/{GRANT}/events", query_params={"limit": "50", "calendar_id": calendar_id, **WINDOW})
            for calendar_id in CALENDARS
        }
        http.get(event_requests["primary-cal"], _page([_event("evt-1", "primary-cal")]))
        http.get(
            event_requests["holidays-cal"],
            HttpResponse(body=json.dumps({"request_id": "r", "error": {"type": "general", "message": "Not Found"}}), status_code=404),
        )
        http.get(event_requests["team-cal"], _page([_event("evt-2", "team-cal"), _event("evt-3", "team-cal")]))

        output = read(get_source(CONFIG), CONFIG, _catalog(sync_mode))

        assert not output.errors
        assert sorted(message.record.data["id"] for message in output.records) == ["evt-1", "evt-2", "evt-3"]
        assert output.get_stream_statuses(STREAM)[-1].value == "COMPLETE"
        assert not any(message.log.level == Level.ERROR for message in output.logs)
        assert any(message.log.level == Level.INFO and "Skipping events for a calendar" in message.log.message for message in output.logs)
        for request in event_requests.values():
            http.assert_number_of_calls(request, 1)
