# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

from conftest import SOURCE_FOLDER

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {
    "api_key": "test-key",
    "api_server": "us",
    "start_date": "2026-09-01T00:00:00Z",
    "end_date": "2026-09-03T00:00:00Z",
}
BASE_URL = "https://api.us.nylas.com/v3"
START = "1788220800"
END = "1788393600"
# A subscribed public calendar: listed by the grant that subscribed to it, unknown to every other grant.
HOLIDAYS = "en.usa#holiday@group.v.calendar.google.com"
NOT_FOUND = HttpResponse(json.dumps({"request_id": "req-1", "error": {"type": "general", "message": "Not Found"}}), 404)


def data_response(records: list[dict[str, Any]], next_cursor: str | None = None) -> HttpResponse:
    body: dict[str, Any] = {"request_id": "req-1", "data": records}
    if next_cursor:
        body["next_cursor"] = next_cursor
    return HttpResponse(json.dumps(body), 200)


def events_request(grant_id: str, calendar_id: str, start: str = START, page_token: str | None = None) -> HttpRequest:
    params = {"limit": "50", "calendar_id": calendar_id, "start": start, "end": END}
    if page_token:
        params["page_token"] = page_token
    return HttpRequest(f"{BASE_URL}/grants/{grant_id}/events", query_params=params)


def mock_grants_and_calendars(http_mocker: HttpMocker, calendars_by_grant: dict[str, list[str]]) -> None:
    http_mocker.get(
        HttpRequest(f"{BASE_URL}/grants", query_params={"limit": "50"}),
        data_response([{"id": grant_id} for grant_id in calendars_by_grant]),
    )
    for grant_id, calendar_ids in calendars_by_grant.items():
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/grants/{grant_id}/calendars", query_params={"limit": "50"}),
            data_response([{"id": calendar_id, "grant_id": grant_id} for calendar_id in calendar_ids]),
        )


def read_events(state: list[AirbyteStateMessage] | None = None) -> EntrypointOutput:
    source = YamlDeclarativeSource(path_to_yaml=str(SOURCE_FOLDER / "manifest.yaml"), config=CONFIG, state=state)
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    return read(source, CONFIG, catalog, state=state)


def event(event_id: str, updated_at: int) -> dict[str, Any]:
    return {"id": event_id, "updated_at": updated_at}


def test_events_are_requested_only_for_each_grants_own_calendars(http_mocker: HttpMocker) -> None:
    mock_grants_and_calendars(http_mocker, {"grant-a": ["a@example.com", HOLIDAYS], "grant-b": ["b@example.com"]})
    own_calendar_requests = [
        events_request("grant-a", "a@example.com"),
        events_request("grant-a", "a@example.com", page_token="page-2"),
        events_request("grant-a", HOLIDAYS),
        events_request("grant-b", "b@example.com"),
    ]
    http_mocker.get(own_calendar_requests[0], data_response([event("a-1", 1788300000)], next_cursor="page-2"))
    http_mocker.get(own_calendar_requests[1], data_response([event("a-2", 1788300100)]))
    http_mocker.get(own_calendar_requests[2], data_response([event("holiday-1", 1788300200)]))
    http_mocker.get(own_calendar_requests[3], data_response([event("b-1", 1788300300)]))
    # Nylas answers 404 when a grant is asked for a calendar it does not have.
    foreign_calendar_requests = [
        events_request("grant-a", "b@example.com"),
        events_request("grant-b", "a@example.com"),
        events_request("grant-b", HOLIDAYS),
    ]
    for request in foreign_calendar_requests:
        http_mocker.get(request, NOT_FOUND)

    output = read_events()

    assert output.errors == []
    assert sorted(record.record.data["id"] for record in output.records) == ["a-1", "a-2", "b-1", "holiday-1"]
    for request in own_calendar_requests:
        http_mocker.assert_number_of_calls(request, 1)
    for request in foreign_calendar_requests:
        http_mocker.assert_number_of_calls(request, 0)


def test_state_saved_by_0_0_77_resumes_each_calendar_from_its_own_cursor(http_mocker: HttpMocker) -> None:
    # Verbatim shape of the `events` state emitted by 0.0.77 for one grant with two calendars.
    legacy_state = {
        "use_global_cursor": False,
        "states": [
            {"partition": {"calendar_id": "cal-1", "grant_id": "grant-a", "parent_slice": {}}, "cursor": {"updated_at": "1788300000"}},
            {"partition": {"calendar_id": "cal-2", "grant_id": "grant-a", "parent_slice": {}}, "cursor": {"updated_at": "1788250000"}},
        ],
        "state": {"updated_at": "1788300000"},
        "lookback_window": 1,
    }
    mock_grants_and_calendars(http_mocker, {"grant-a": ["cal-1", "cal-2"]})
    http_mocker.get(events_request("grant-a", "cal-1", start="1788300000"), data_response([event("cal-1-new", 1788310000)]))
    # Without the migration cal-2 would resume from the newest cursor of all calendars (start=1788299999).
    http_mocker.get(events_request("grant-a", "cal-2", start="1788250000"), data_response([event("cal-2-new", 1788260000)]))

    output = read_events(StateBuilder().with_stream_state("events", legacy_state).build())

    assert output.errors == []
    assert sorted(record.record.data["id"] for record in output.records) == ["cal-1-new", "cal-2-new"]
    final_state = output.most_recent_state.stream_state.__dict__
    assert sorted(final_state["states"], key=lambda state: state["partition"]["calendar_id"]) == [
        {
            "partition": {"calendar_id": "cal-1", "parent_slice": {"grant_id": "grant-a", "parent_slice": {}}},
            "cursor": {"updated_at": "1788310000"},
        },
        {
            "partition": {"calendar_id": "cal-2", "parent_slice": {"grant_id": "grant-a", "parent_slice": {}}},
            "cursor": {"updated_at": "1788260000"},
        },
    ]
