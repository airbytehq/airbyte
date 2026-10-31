# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the date window of the `events` stream.

`end_date` used to be a required spec field, so every connection was pinned to a
fixed upper bound and incremental syncs silently stopped returning events past it.
`end_date` is now optional and defaults to the current time, so a connection
without it keeps syncing new events.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_NOW = "2026-10-31T00:00:00Z"
_NOW_EPOCH = "1793404800"
_START_DATE_EPOCH = "1788220800"  # 2026-09-01T00:00:00Z
_END_DATE_EPOCH = "1789430400"  # 2026-09-15T00:00:00Z

_BASE_CONFIG = {"api_key": "key", "api_server": "us", "start_date": "2026-09-01T00:00:00Z"}

_GRANT_ID = "grant-1"
_CALENDAR_ID = "calendar-1"
_BASE_URL = "https://api.us.nylas.com/v3"


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": records, "next_cursor": None}), status_code=200)


def _event(event_id: str, updated_at: int) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": _GRANT_ID, "calendar_id": _CALENDAR_ID, "updated_at": updated_at, "title": event_id}


def _mock_parents(http_mocker: HttpMocker) -> None:
    http_mocker.get(HttpRequest(f"{_BASE_URL}/grants", query_params={"limit": "50"}), _page([{"id": _GRANT_ID}]))
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/grants/{_GRANT_ID}/calendars", query_params={"limit": "50"}),
        _page([{"id": _CALENDAR_ID, "grant_id": _GRANT_ID}]),
    )


def _events_request(start: str, end: str) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}/grants/{_GRANT_ID}/events",
        query_params={"limit": "50", "calendar_id": _CALENDAR_ID, "start": start, "end": end},
    )


def _read(config: Dict[str, Any], state: Optional[List[Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(name="events", sync_mode=SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config, catalog, state)


@freeze_time(_NOW)
class EventsDateWindowTest(TestCase):
    @HttpMocker()
    def test_without_end_date_window_ends_now(self, http_mocker: HttpMocker) -> None:
        _mock_parents(http_mocker)
        http_mocker.get(_events_request(_START_DATE_EPOCH, _NOW_EPOCH), _page([_event("october-event", 1792000000)]))

        output = _read(_BASE_CONFIG)

        assert not output.errors, output.errors
        assert [r.record.data["id"] for r in output.records] == ["october-event"]

    @HttpMocker()
    def test_without_end_date_resumes_from_state_past_old_end_date(self, http_mocker: HttpMocker) -> None:
        _mock_parents(http_mocker)
        state_epoch = "1789387200"  # 2026-09-14T12:00:00Z
        state = (
            StateBuilder()
            .with_stream_state(
                "events",
                {
                    "use_global_cursor": False,
                    "state": {"updated_at": state_epoch},
                    "states": [
                        {
                            "partition": {"calendar_id": _CALENDAR_ID, "parent_slice": {"grant_id": _GRANT_ID, "parent_slice": {}}},
                            "cursor": {"updated_at": state_epoch},
                        }
                    ],
                },
            )
            .build()
        )
        http_mocker.get(_events_request(state_epoch, _NOW_EPOCH), _page([_event("october-event", 1792000000)]))

        output = _read(_BASE_CONFIG, state)

        assert not output.errors, output.errors
        assert [r.record.data["id"] for r in output.records] == ["october-event"]

    @HttpMocker()
    def test_explicit_end_date_is_still_honored(self, http_mocker: HttpMocker) -> None:
        _mock_parents(http_mocker)
        http_mocker.get(_events_request(_START_DATE_EPOCH, _END_DATE_EPOCH), _page([_event("september-event", 1788500000)]))

        output = _read({**_BASE_CONFIG, "end_date": "2026-09-15T00:00:00Z"})

        assert not output.errors, output.errors
        assert [r.record.data["id"] for r in output.records] == ["september-event"]


def test_end_date_is_optional_in_spec() -> None:
    spec = get_source(config=_BASE_CONFIG).spec(None).connectionSpecification
    assert "end_date" in spec["properties"]
    assert "end_date" not in spec["required"]
