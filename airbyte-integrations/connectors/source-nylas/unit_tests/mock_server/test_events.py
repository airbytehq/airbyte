# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
GRANT_ID = "grant-1"
HOLIDAY_CALENDAR_ID = "en.usa#holiday@group.v.calendar.google.com"
NOT_FOUND_BODY = {"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}


def events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        f"{BASE_URL}/grants/{GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": calendar_id, "start": "1788220800", "end": "1788393600"},
    )


def data_response(records: list[dict]) -> HttpResponse:
    return HttpResponse(json.dumps({"request_id": "req-1", "data": records}))


def read_events() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )
    return read(source, config=CONFIG, catalog=catalog, state=[])


def test_calendar_answering_404_is_skipped_and_other_calendars_still_sync() -> None:
    calendar_ids = ["primary@example.com", HOLIDAY_CALENDAR_ID, "team@example.com"]
    holiday_events_request = events_request(HOLIDAY_CALENDAR_ID)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/grants", query_params={"limit": "50"}),
            data_response([{"id": GRANT_ID, "provider": "google"}]),
        )
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/grants/{GRANT_ID}/calendars", query_params={"limit": "50"}),
            data_response([{"id": calendar_id, "grant_id": GRANT_ID} for calendar_id in calendar_ids]),
        )
        http_mocker.get(
            events_request("primary@example.com"),
            data_response([{"id": "event-primary", "calendar_id": "primary@example.com", "updated_at": 1788300000}]),
        )
        http_mocker.get(holiday_events_request, HttpResponse(json.dumps(NOT_FOUND_BODY), 404))
        http_mocker.get(
            events_request("team@example.com"),
            data_response([{"id": "event-team", "calendar_id": "team@example.com", "updated_at": 1788300001}]),
        )

        output = read_events()

        # The 404 is not retried: the holiday calendar is requested exactly once.
        http_mocker.assert_number_of_calls(holiday_events_request, 1)

    assert sorted(record.record.data["id"] for record in output.records) == ["event-primary", "event-team"]
    assert output.errors == []
    assert not any(log.log.level.value == "ERROR" for log in output.logs)
    assert output.get_stream_statuses("events")[-1] == AirbyteStreamStatus.COMPLETE
