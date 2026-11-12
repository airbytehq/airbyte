# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `events` stream of `source-nylas`.

`events` is read per calendar, and a calendar belongs to exactly one grant. Nylas
answers 404 when a grant is asked for a calendar it does not have, so the stream
must only pair a calendar with the grant that listed it.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder


_START = "1788220800"  # 2026-09-01T00:00:00Z, the configured start_date
_END = "1788393600"  # 2026-09-03T00:00:00Z, the configured end_date

_WORK_CALENDAR = "ada@example.com"
# Google subscribed calendars use ids like this one; the `#` and `@` must reach Nylas URL-encoded.
_HOLIDAY_CALENDAR = "en.usa#holiday@group.v.calendar.google.com"
_OTHER_CALENDAR = "grace@example.com"

# Which calendars each grant lists. No calendar is shared between the two grants.
_CALENDARS_BY_GRANT = {
    "grant-1": [_WORK_CALENDAR, _HOLIDAY_CALENDAR],
    "grant-2": [_OTHER_CALENDAR],
}


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"request_id": "req-1", "data": records}), status_code=200)


def _events_request(grant_id: str, calendar_id: str, start: str = _START) -> HttpRequest:
    return (
        NylasRequestBuilder.events_endpoint(grant_id)
        .with_query_param("calendar_id", calendar_id)
        .with_query_param("start", start)
        .with_query_param("end", _END)
        .build()
    )


def _event(event_id: str, grant_id: str, calendar_id: str, updated_at: int) -> Dict[str, Any]:
    return {"id": event_id, "grant_id": grant_id, "calendar_id": calendar_id, "object": "event", "updated_at": updated_at}


def _given_grants_and_calendars(http_mocker: HttpMocker) -> None:
    http_mocker.get(NylasRequestBuilder.grants_endpoint().build(), _page([{"id": grant_id} for grant_id in _CALENDARS_BY_GRANT]))
    for grant_id, calendar_ids in _CALENDARS_BY_GRANT.items():
        http_mocker.get(
            NylasRequestBuilder.calendars_endpoint(grant_id).build(),
            _page([{"id": calendar_id, "grant_id": grant_id} for calendar_id in calendar_ids]),
        )


def _read(state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("events", SyncMode.incremental).build()
    airbyte_state = StateBuilder().with_stream_state("events", state).build() if state else StateBuilder().build()
    return read(get_source(config=config, state=airbyte_state), config=config, catalog=catalog, state=airbyte_state)


def _partition_cursors(output: EntrypointOutput) -> Dict[tuple, str]:
    """Map (grant_id, calendar_id) to the cursor in the last emitted `events` state."""
    # AirbyteStateBlob nests further blobs, so flatten it to plain dicts before indexing.
    stream_state = json.loads(json.dumps(output.most_recent_state.stream_state, default=lambda blob: blob.__dict__))
    return {
        (state["partition"]["parent_slice"]["grant_id"], state["partition"]["calendar_id"]): state["cursor"]["updated_at"]
        for state in stream_state["states"]
    }


class TestEvents(TestCase):
    @HttpMocker()
    def test_events_are_requested_only_for_the_calendars_of_their_own_grant(self, http_mocker: HttpMocker) -> None:
        """
        Only the three (grant, calendar) pairs that exist are mocked. Asking any grant for
        another grant's calendar has no mock, which fails the read the way Nylas' 404 does.
        """
        _given_grants_and_calendars(http_mocker)
        http_mocker.get(_events_request("grant-1", _WORK_CALENDAR), _page([_event("event-work", "grant-1", _WORK_CALENDAR, 1788250000)]))
        http_mocker.get(
            _events_request("grant-1", _HOLIDAY_CALENDAR), _page([_event("event-holiday", "grant-1", _HOLIDAY_CALENDAR, 1788260000)])
        )
        http_mocker.get(_events_request("grant-2", _OTHER_CALENDAR), _page([_event("event-other", "grant-2", _OTHER_CALENDAR, 1788270000)]))

        output = _read()

        assert output.errors == []
        assert sorted(record.record.data["id"] for record in output.records) == ["event-holiday", "event-other", "event-work"]
        assert _partition_cursors(output) == {
            ("grant-1", _WORK_CALENDAR): "1788250000",
            ("grant-1", _HOLIDAY_CALENDAR): "1788260000",
            ("grant-2", _OTHER_CALENDAR): "1788270000",
        }

    @HttpMocker()
    def test_state_saved_with_grant_and_calendar_partitions_resumes_each_calendar_from_its_own_cursor(
        self, http_mocker: HttpMocker
    ) -> None:
        """
        State saved by versions up to 0.0.77 keys partitions by `grant_id` and `calendar_id` side by side.
        Each calendar must still resume from its own cursor rather than from the stream-wide one.
        """
        legacy_state = {
            "use_global_cursor": False,
            "states": [
                {
                    "partition": {"calendar_id": _WORK_CALENDAR, "grant_id": "grant-1", "parent_slice": {}},
                    "cursor": {"updated_at": "1788250000"},
                },
                {
                    "partition": {"calendar_id": _HOLIDAY_CALENDAR, "grant_id": "grant-1", "parent_slice": {}},
                    "cursor": {"updated_at": "1788260000"},
                },
                {
                    "partition": {"calendar_id": _OTHER_CALENDAR, "grant_id": "grant-2", "parent_slice": {}},
                    "cursor": {"updated_at": "1788270000"},
                },
            ],
            "state": {"updated_at": "1788270000"},
            "lookback_window": 0,
        }
        _given_grants_and_calendars(http_mocker)
        http_mocker.get(
            _events_request("grant-1", _WORK_CALENDAR, start="1788250000"),
            _page([_event("event-work-2", "grant-1", _WORK_CALENDAR, 1788300000)]),
        )
        http_mocker.get(_events_request("grant-1", _HOLIDAY_CALENDAR, start="1788260000"), _page([]))
        http_mocker.get(
            _events_request("grant-2", _OTHER_CALENDAR, start="1788270000"),
            _page([_event("event-other-2", "grant-2", _OTHER_CALENDAR, 1788310000)]),
        )

        output = _read(state=legacy_state)

        assert output.errors == []
        assert sorted(record.record.data["id"] for record in output.records) == ["event-other-2", "event-work-2"]
        assert _partition_cursors(output) == {
            ("grant-1", _WORK_CALENDAR): "1788300000",
            ("grant-1", _HOLIDAY_CALENDAR): "1788260000",
            ("grant-2", _OTHER_CALENDAR): "1788310000",
        }
