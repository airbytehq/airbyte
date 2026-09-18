# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from uuid import UUID

import pytest
from source_posthog.components import EventsRetriever
from test_pagination import BASE, stream

from airbyte_cdk.models import SyncMode


SLICE = {"project_id": "42", "start_time": "2026-09-01T00:00:00Z", "end_time": "2026-09-03T00:00:00Z"}


def event(number, timestamp="2026-09-02T12:00:00.123456Z"):
    return {"id": str(UUID(int=number)), "timestamp": timestamp, "properties": {"nested": [1, {"keep": True}]}}


def read(events):
    return list(events.read_records(SyncMode.incremental, stream_slice=SLICE))


@pytest.mark.parametrize("page_size", [1000, 50])
def test_tied_timestamps_and_false_terminal_page(requests_mock, page_size):
    records = [event(i) for i in range(1, 1004)] + [event(2000, "2026-09-02T13:00:00Z")]
    calls = []

    def page(request, context):
        params = request.qs
        assert params["limit"] == ["1000"]
        assert json.loads(params["orderby"][0]) == ["timestamp", "uuid"]
        assert params["after"] == ["2026-08-31t23:59:59.999999+00:00"]
        assert params["before"] == [SLICE["end_time"].lower()]
        if calls:
            expression = json.loads(params["properties"][0])[0]["key"]
            previous = calls[-1][-1]
            assert str(UUID(previous["id"])) in expression
            timestamp = EventsRetriever._timestamp(previous["timestamp"]).isoformat(timespec="microseconds").lower()
            assert timestamp in expression
        start = sum(len(batch) for batch in calls)
        batch = records[start : start + page_size]
        calls.append(batch)
        return {"results": batch, "next": None}

    requests_mock.get(BASE + "events/", json=page)
    events = stream("events")
    assert [dict(r) for r in read(events)] == records
    assert calls[-1] == []
    assert events.state == {"42": {"timestamp": records[-1]["timestamp"]}}


def test_clickhouse_uuid_order_and_slice_start_are_preserved(requests_mock):
    records = [event(1 << 64, SLICE["start_time"]), event(1, SLICE["start_time"])]
    requests_mock.get(BASE + "events/", [{"json": {"results": records}}, {"json": {"results": []}}])
    assert [dict(r) for r in read(stream("events"))] == records


@pytest.mark.parametrize(
    "bad_page",
    [
        [event(1)],
        [event(3), event(2)],
        [event(4, "2026-09-03T00:00:00Z")],
        [event(4, "2026-08-31T23:59:59Z")],
        [{"id": "not-a-uuid", "timestamp": "2026-09-02T12:00:00Z"}],
        [event(4, "2026-09-02T12:00:00")],
    ],
)
def test_invalid_or_nonprogressing_page_does_not_checkpoint(requests_mock, bad_page):
    requests_mock.get(BASE + "events/", [{"json": {"results": [event(1)]}}, {"json": {"results": bad_page}}])
    events = stream("events")
    old = {"42": {"timestamp": SLICE["start_time"]}}
    events.state = old.copy()
    iterator = events.read_records(SyncMode.incremental, stream_slice=SLICE)
    assert dict(next(iterator)) == event(1)
    with pytest.raises((ValueError, KeyError)):
        next(iterator)
    assert events.state == old


def test_missing_results_is_not_treated_as_success(requests_mock):
    requests_mock.get(BASE + "events/", json={"error": "bad response"})
    events = stream("events")
    with pytest.raises(ValueError, match="invalid events page"):
        read(events)
    assert events.state == {}


def test_lookback_replays_saved_state_without_rewinding_checkpoint(requests_mock):
    requests_mock.get("https://app.posthog.com/api/projects", json={"results": [{"id": 42}], "next": None})
    events = stream("events", events_lookback_hours=24)
    state = {"42": {"timestamp": "2026-09-02T12:00:00.123456Z"}}
    events.state = state.copy()
    slices = list(events.stream_slices(sync_mode=SyncMode.incremental))
    assert EventsRetriever._timestamp(slices[0]["start_time"]) == EventsRetriever._timestamp("2026-09-01T12:00:00.123456Z")
    events.retriever.cursor.close_slice(slices[0], event(1, "2026-09-01T13:00:00Z"))
    assert events.state == state


def test_legacy_state_does_not_rewind_when_replaying_older_events():
    events = stream("events")
    old_timestamp = "2026-09-02T12:00:00Z"
    events.state = {"timestamp": old_timestamp}
    events.retriever.cursor.close_slice(SLICE, event(1, "2026-09-01T12:00:00Z"))
    assert events.state["42"]["timestamp"] == old_timestamp
