# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_API = "https://api.us.nylas.com/v3"
_CONFIG = {"api_key": "test-key", "api_server": "us", "start_date": "2026-09-01T00:00:00Z", "end_date": "2026-09-03T00:00:00Z"}
_START = "1788220800"  # 2026-09-01T00:00:00Z
_END = "1788393600"  # 2026-09-03T00:00:00Z

_PRIMARY = "ada@example.com"
_HOLIDAYS = "en.usa#holiday@group.v.calendar.google.com"
_OTHER_PRIMARY = "grace@example.com"


def _read(state: Optional[List[Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    return read(get_source(_CONFIG, catalog, state), _CONFIG, catalog, state)


def _mock_grants(http_mocker: HttpMocker, calendars_by_grant: Mapping[str, List[str]]) -> None:
    http_mocker.get(
        HttpRequest(f"{_API}/grants", query_params={"limit": "50"}),
        HttpResponse(json.dumps({"data": [{"id": grant_id} for grant_id in calendars_by_grant]})),
    )
    for grant_id, calendar_ids in calendars_by_grant.items():
        http_mocker.get(
            HttpRequest(f"{_API}/grants/{grant_id}/calendars", query_params={"limit": "50"}),
            HttpResponse(json.dumps({"data": [{"id": calendar_id, "grant_id": grant_id} for calendar_id in calendar_ids]})),
        )


def _mock_events(http_mocker: HttpMocker, grant_id: str, calendar_id: str, start: str, event_id: str, updated_at: int) -> None:
    http_mocker.get(
        HttpRequest(
            f"{_API}/grants/{grant_id}/events",
            query_params={"limit": "50", "calendar_id": calendar_id, "start": start, "end": _END},
        ),
        HttpResponse(json.dumps({"data": [{"id": event_id, "calendar_id": calendar_id, "grant_id": grant_id, "updated_at": updated_at}]})),
    )


def _event_requests(http_mocker: HttpMocker) -> List[str]:
    return sorted(request.url for request in http_mocker._mocker.request_history if request.path.endswith("/events"))


def _partition_states(output: EntrypointOutput) -> List[Mapping[str, Any]]:
    states = output.most_recent_state.stream_state.__dict__["states"]
    return sorted(states, key=lambda state: state["partition"]["calendar_id"])


def test_events_are_requested_for_each_calendar_under_its_own_grant_only() -> None:
    # Nylas answers 404 when a calendar is requested under a grant that does not have it, so the only
    # events requests mocked here are the three (grant, calendar) pairs that the calendars stream lists.
    with HttpMocker() as http_mocker:
        _mock_grants(http_mocker, {"grant-ada": [_PRIMARY, _HOLIDAYS], "grant-grace": [_OTHER_PRIMARY]})
        _mock_events(http_mocker, "grant-ada", _PRIMARY, _START, "evt-ada-primary", 1788300000)
        _mock_events(http_mocker, "grant-ada", _HOLIDAYS, _START, "evt-ada-holiday", 1788300100)
        _mock_events(http_mocker, "grant-grace", _OTHER_PRIMARY, _START, "evt-grace-primary", 1788300200)

        output = _read()

        assert _event_requests(http_mocker) == [
            f"{_API}/grants/grant-ada/events?limit=50&calendar_id=ada%40example.com&start={_START}&end={_END}",
            f"{_API}/grants/grant-ada/events?limit=50&calendar_id=en.usa%23holiday%40group.v.calendar.google.com&start={_START}&end={_END}",
            f"{_API}/grants/grant-grace/events?limit=50&calendar_id=grace%40example.com&start={_START}&end={_END}",
        ]
    assert output.errors == []
    assert sorted(record.record.data["id"] for record in output.records) == ["evt-ada-holiday", "evt-ada-primary", "evt-grace-primary"]


def test_state_saved_before_the_partitioning_change_resumes_each_calendar_from_its_own_cursor() -> None:
    # State shape emitted by versions <= 0.0.77, where grant_id sat next to calendar_id in the partition.
    legacy_state = {
        "use_global_cursor": False,
        "states": [
            {"partition": {"calendar_id": _PRIMARY, "grant_id": "grant-ada", "parent_slice": {}}, "cursor": {"updated_at": "1788250000"}},
            {"partition": {"calendar_id": _HOLIDAYS, "grant_id": "grant-ada", "parent_slice": {}}, "cursor": {"updated_at": "1788300000"}},
        ],
        "state": {"updated_at": "1788300000"},
        "lookback_window": 1,
    }
    with HttpMocker() as http_mocker:
        _mock_grants(http_mocker, {"grant-ada": [_PRIMARY, _HOLIDAYS]})
        _mock_events(http_mocker, "grant-ada", _PRIMARY, "1788250000", "evt-ada-primary", 1788260000)
        _mock_events(http_mocker, "grant-ada", _HOLIDAYS, "1788300000", "evt-ada-holiday", 1788310000)

        output = _read(StateBuilder().with_stream_state("events", legacy_state).build())

        # The primary calendar resumes from its own cursor (1788250000), not from the newer global cursor.
        assert _event_requests(http_mocker) == [
            f"{_API}/grants/grant-ada/events?limit=50&calendar_id=ada%40example.com&start=1788250000&end={_END}",
            f"{_API}/grants/grant-ada/events?limit=50&calendar_id=en.usa%23holiday%40group.v.calendar.google.com&start=1788300000&end={_END}",
        ]
    assert output.errors == []
    assert sorted(record.record.data["id"] for record in output.records) == ["evt-ada-holiday", "evt-ada-primary"]
    assert _partition_states(output) == [
        {
            "partition": {"calendar_id": _PRIMARY, "parent_slice": {"grant_id": "grant-ada", "parent_slice": {}}},
            "cursor": {"updated_at": "1788260000"},
        },
        {
            "partition": {"calendar_id": _HOLIDAYS, "parent_slice": {"grant_id": "grant-ada", "parent_slice": {}}},
            "cursor": {"updated_at": "1788310000"},
        },
    ]
