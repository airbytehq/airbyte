# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter
from datetime import datetime, timedelta, timezone

import pytest
from _helpers import CONFIG, ORGANIZATION_URI, collection, invitees_request, list_request, mock_user, read_stream
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder


LEGACY_SCHEDULED_EVENTS_STATE = {
    "lookback_window": 0,
    "parent_state": {},
    "state": {"start_time": "2024-03-01T00:00:00.000000Z"},
    "states": [
        {
            "cursor": {"start_time": "2024-03-01T00:00:00.000000Z"},
            "partition": {
                "organization_uri": ORGANIZATION_URI,
                "parent_slice": {},
            },
        }
    ],
    "use_global_cursor": False,
}
LEGACY_EVENT_INVITEES_STATE = {
    "lookback_window": 0,
    "parent_state": {"scheduled_events": LEGACY_SCHEDULED_EVENTS_STATE},
    "state": {"created_at": "2024-01-31T23:00:00.000000Z"},
    "states": [
        {
            "cursor": {"created_at": "2024-01-31T23:00:00.000000Z"},
            "partition": {
                "parent_slice": {
                    "organization_uri": ORGANIZATION_URI,
                    "parent_slice": {},
                },
                "scheduled_event_id": "legacy-future",
            },
        }
    ],
    "use_global_cursor": False,
}
LEGACY_STATES = {
    "scheduled_events": LEGACY_SCHEDULED_EVENTS_STATE,
    "event_invitees": LEGACY_EVENT_INVITEES_STATE,
}


def calendly_event(event_id: str, start_time: str, updated_at: str) -> dict[str, str]:
    return {
        "uri": f"https://api.calendly.com/scheduled_events/{event_id}",
        "start_time": start_time,
        "created_at": updated_at,
        "updated_at": updated_at,
        "status": "active",
    }


def emitted_state(output, stream_name: str):
    state = output.most_recent_state
    assert state.stream_descriptor.name == stream_name
    return StateBuilder().with_stream_state(stream_name, state.stream_state).build()


def records(output) -> list[dict]:
    return [record.record.data for record in output.records]


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def state_field(value, key: str):
    return value.get(key) if isinstance(value, dict) else getattr(value, key, None)


def parent_updated_at(output, stream_name: str) -> str:
    state = output.most_recent_state.stream_state
    if stream_name == "scheduled_events":
        return state_field(state_field(state, "state"), "updated_at")
    parent = state_field(state, "parent_state")
    scheduled_events = state_field(parent, "scheduled_events")
    return state_field(state_field(scheduled_events, "state"), "updated_at")


def test_future_event_uses_updated_at_and_lookback_reemits_unchanged_event_within_window() -> None:
    sync_time = datetime(2024, 2, 1, tzinfo=timezone.utc)
    future_event = calendly_event("future", "2024-03-01T00:00:00.000000Z", "2024-01-31T19:58:00.000000Z")
    cursor_event = calendly_event("cursor", "2024-03-02T00:00:00.000000Z", "2024-01-31T20:00:00.000000Z")
    target = list_request("scheduled_events")
    with freeze_time(sync_time) as clock, HttpMocker() as http:
        mock_user(http)
        http.get(target, [collection([future_event, cursor_event]), collection([future_event, cursor_event])])

        first = read_stream("scheduled_events")
        assert not first.errors
        assert Counter(record["id"] for record in records(first)) == Counter({"future": 1, "cursor": 1})
        first_state = emitted_state(first, "scheduled_events")
        cursor_time = parse_time(parent_updated_at(first, "scheduled_events"))
        future_event_updated_at = parse_time(future_event["updated_at"])
        assert cursor_time == parse_time(cursor_event["updated_at"])
        assert timedelta(0) < cursor_time - future_event_updated_at <= timedelta(minutes=5)

        clock.tick(delta=timedelta(minutes=1))
        second = read_stream("scheduled_events", state=first_state)

        assert not second.errors
        http.assert_number_of_calls(target, 2)
        assert Counter(record["id"] for record in records(second)) == Counter({"future": 1, "cursor": 1})
        assert cursor_time <= sync_time


def test_booking_for_earlier_time_is_emitted_once_after_first_sync() -> None:
    future_event = calendly_event("future", "2024-03-01T00:00:00.000000Z", "2024-01-30T20:00:00.000000Z")
    cursor_event = calendly_event("cursor", "2024-03-02T00:00:00.000000Z", "2024-01-31T20:00:00.000000Z")
    new_booking = calendly_event("earlier-booking", "2024-02-02T00:00:00.000000Z", "2024-02-01T00:00:30.000000Z")
    target = list_request("scheduled_events")
    with freeze_time("2024-02-01T00:00:00Z") as clock, HttpMocker() as http:
        mock_user(http)
        http.get(target, [collection([future_event, cursor_event]), collection([future_event, cursor_event, new_booking])])

        first = read_stream("scheduled_events")
        assert not first.errors
        assert Counter(record["id"] for record in records(first)) == Counter({"future": 1, "cursor": 1})
        first_state = emitted_state(first, "scheduled_events")
        assert parent_updated_at(first, "scheduled_events") == cursor_event["updated_at"]

        clock.tick(delta=timedelta(minutes=1))
        second = read_stream("scheduled_events", state=first_state)

        assert not second.errors
        assert Counter(record["id"] for record in records(second)) == Counter({"cursor": 1, "earlier-booking": 1})
        http.assert_number_of_calls(target, 2)


def test_cancellation_of_synced_future_event_is_emitted_once() -> None:
    active_event = calendly_event("future", "2024-03-01T00:00:00.000000Z", "2024-01-31T20:00:00.000000Z")
    canceled_event = {
        **calendly_event("future", "2024-03-01T00:00:00.000000Z", "2024-02-01T00:00:30.000000Z"),
        "status": "canceled",
    }
    target = list_request("scheduled_events")
    with freeze_time("2024-02-01T00:00:00Z") as clock, HttpMocker() as http:
        mock_user(http)
        http.get(target, [collection([active_event]), collection([canceled_event])])

        first = read_stream("scheduled_events")
        assert not first.errors
        assert [record["id"] for record in records(first)] == ["future"]
        first_state = emitted_state(first, "scheduled_events")

        clock.tick(delta=timedelta(minutes=1))
        second = read_stream("scheduled_events", state=first_state)

        assert not second.errors
        emitted = records(second)
        assert [record["id"] for record in emitted] == ["future"]
        assert emitted[0]["status"] == "canceled"
        http.assert_number_of_calls(target, 2)


def test_new_invitee_follows_only_changed_parent_event() -> None:
    unchanged_event = calendly_event("unchanged", "2024-03-02T00:00:00.000000Z", "2024-01-30T20:00:00.000000Z")
    changed_event = calendly_event("changed", "2024-03-01T00:00:00.000000Z", "2024-01-31T20:00:00.000000Z")
    updated_event = calendly_event("changed", "2024-03-01T00:00:00.000000Z", "2024-02-01T00:00:30.000000Z")
    scheduled_events_request = list_request("scheduled_events")
    unchanged_invitees_request = invitees_request("unchanged")
    changed_invitees_request = invitees_request("changed")
    existing_invitee = {
        "uri": "https://api.calendly.com/invitees/changed-old",
        "created_at": "2024-01-10T00:00:00.000000Z",
        "updated_at": "2024-01-10T00:00:00.000000Z",
    }
    latest_existing_invitee = {
        "uri": "https://api.calendly.com/invitees/changed-latest",
        "created_at": "2024-01-25T00:00:00.000000Z",
        "updated_at": "2024-01-25T00:00:00.000000Z",
    }
    new_invitee = {
        "uri": "https://api.calendly.com/invitees/changed-new",
        "created_at": "2024-02-01T00:00:30.000000Z",
        "updated_at": "2024-02-01T00:00:30.000000Z",
    }
    with freeze_time("2024-02-01T00:00:00Z") as clock, HttpMocker() as http:
        mock_user(http)
        http.get(scheduled_events_request, [collection([changed_event, unchanged_event]), collection([updated_event, unchanged_event])])
        http.get(unchanged_invitees_request, collection([]))
        http.get(
            changed_invitees_request,
            [
                collection([existing_invitee, latest_existing_invitee]),
                collection([existing_invitee, latest_existing_invitee, new_invitee]),
            ],
        )

        first = read_stream("event_invitees")
        assert not first.errors
        first_state = emitted_state(first, "event_invitees")

        clock.tick(delta=timedelta(minutes=1))
        second = read_stream("event_invitees", state=first_state)

        assert not second.errors
        assert [record["uri"] for record in records(second)] == [
            existing_invitee["uri"],
            latest_existing_invitee["uri"],
            new_invitee["uri"],
        ]
        http.assert_number_of_calls(scheduled_events_request, 2)
        http.assert_number_of_calls(unchanged_invitees_request, 1)
        http.assert_number_of_calls(changed_invitees_request, 2)


@pytest.mark.parametrize("stream_name", ["scheduled_events", "event_invitees"])
def test_legacy_state_resumes_from_start_date_and_emits_updated_at_state(stream_name: str) -> None:
    event_record = calendly_event("legacy-future", "2024-03-01T00:00:00.000000Z", "2024-01-31T20:00:00.000000Z")
    scheduled_events_request = list_request("scheduled_events")
    state = StateBuilder().with_stream_state(stream_name, LEGACY_STATES[stream_name]).build()
    with freeze_time("2024-02-01T00:00:00Z"), HttpMocker() as http:
        mock_user(http)
        http.get(scheduled_events_request, collection([event_record]))
        if stream_name == "event_invitees":
            invitee_request = invitees_request("legacy-future")
            http.get(
                invitee_request,
                collection(
                    [
                        {
                            "uri": "https://api.calendly.com/invitees/legacy-new",
                            "created_at": "2024-02-01T00:00:00.000000Z",
                            "updated_at": "2024-02-01T00:00:00.000000Z",
                        }
                    ]
                ),
            )

        output = read_stream(stream_name, state=state)

        assert not output.errors
        assert records(output)
        assert parent_updated_at(output, stream_name) == event_record["updated_at"]
        http.assert_number_of_calls(scheduled_events_request, 1)
        if stream_name == "event_invitees":
            http.assert_number_of_calls(invitee_request, 1)
