# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from _helpers import CONFIG, USER, collection, event, invitees_request, list_request, mock_user, read_stream

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder


def test_api_user_reads_resource() -> None:
    with HttpMocker() as http:
        target = mock_user(http)
        output = read_stream("api_user")
        assert not output.errors
        assert [r.record.data for r in output.records] == [USER]
        http.assert_number_of_calls(target, 1)


def read_paginated_list(stream: str) -> None:
    records = [{"uri": f"https://api.calendly.com/{stream}/{index}", "updated_at": "2024-01-15T00:00:00.000000Z"} for index in [1, 2]]
    with HttpMocker() as http:
        user = mock_user(http)
        first = list_request(stream)
        second = list_request(stream, "next-token")
        http.get(first, collection([records[0]], "next-token"))
        http.get(second, collection([records[1]]))
        output = read_stream(stream)
        assert not output.errors
        assert {r.record.data["uri"] for r in output.records} == {r["uri"] for r in records}
        http.assert_number_of_calls(user, 1)
        http.assert_number_of_calls(first, 1)
        http.assert_number_of_calls(second, 1)


def test_event_types_pages_with_organization_and_sort() -> None:
    read_paginated_list("event_types")


def test_groups_pages_with_organization() -> None:
    read_paginated_list("groups")


def test_organization_memberships_pages_with_organization_and_sort() -> None:
    read_paginated_list("organization_memberships")


@pytest.mark.parametrize(
    "lookback,minimum",
    [
        ({}, "2024-01-20T00:00:00.000000Z"),
        ({"lookback_days": 0}, "2024-01-20T00:00:00.000000Z"),
        ({"lookback_days": 2}, "2024-01-18T00:00:00.000000Z"),
        ({"lookback_days": 7}, "2024-01-13T00:00:00.000000Z"),
    ],
)
def test_scheduled_events_pages_from_state_minus_lookback(lookback: dict, minimum: str) -> None:
    state = StateBuilder().with_stream_state("scheduled_events", {"start_time": "2024-01-20T00:00:00.000000Z"}).build()
    records = [{**event(name), "start_time": f"2024-01-{day}T00:00:00.000000Z"} for name, day in [("one", 22), ("two", 21)]]
    first = list_request("scheduled_events", min_start_time=minimum)
    second = list_request("scheduled_events", "next-token", min_start_time=minimum)
    with HttpMocker() as http:
        mock_user(http)
        http.get(first, collection([records[0]], "next-token"))
        http.get(second, collection([records[1]]))
        output = read_stream("scheduled_events", {**CONFIG, **lookback}, state)
        assert not output.errors
        assert {r.record.data["id"] for r in output.records} == {"one", "two"}
        http.assert_number_of_calls(first, 1)
        http.assert_number_of_calls(second, 1)


def test_null_lookback_is_rejected_by_the_unchanged_number_spec() -> None:
    with HttpMocker():
        output = read_stream("scheduled_events", {**CONFIG, "lookback_days": None})
        assert not output.records
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert "None is not of type 'number'" in output.errors[0].trace.error.message


def test_event_invitees_pages_for_each_parent_event() -> None:
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("scheduled_events"), collection([event("one")], "parents-next"))
        http.get(list_request("scheduled_events", "parents-next"), collection([event("two")]))
        targets = []
        for parent in ["one", "two"]:
            first = invitees_request(parent)
            second = invitees_request(parent, "invitees-next")
            targets.extend([first, second])
            http.get(
                first,
                collection(
                    [{"uri": f"https://api.calendly.com/invitees/{parent}-1", "created_at": "2024-01-15T00:00:00.000000Z"}], "invitees-next"
                ),
            )
            http.get(
                second,
                collection([{"uri": f"https://api.calendly.com/invitees/{parent}-2", "created_at": "2024-01-15T00:00:00.000000Z"}]),
            )
        output = read_stream("event_invitees")
        assert not output.errors
        assert {(r.record.data["scheduled_event_id"], r.record.data["id"]) for r in output.records} == {
            (parent, f"{parent}-{index}") for parent in ["one", "two"] for index in [1, 2]
        }
        for target in targets:
            http.assert_number_of_calls(target, 1)


@pytest.mark.parametrize("stream", ["event_types", "groups", "organization_memberships", "scheduled_events", "event_invitees"])
def test_empty_collections_complete_without_records(stream: str) -> None:
    with HttpMocker() as http:
        mock_user(http)
        if stream == "event_invitees":
            http.get(list_request("scheduled_events"), collection([event("empty")]))
            target = invitees_request("empty")
        else:
            target = list_request(stream)
        http.get(target, collection([]))
        output = read_stream(stream)
        assert not output.errors
        assert not output.records
        http.assert_number_of_calls(target, 1)
