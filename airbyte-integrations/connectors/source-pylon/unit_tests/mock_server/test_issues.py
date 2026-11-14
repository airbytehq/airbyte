# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter
from datetime import datetime, timedelta, timezone
from threading import Event
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.helpers import BASE, CONFIG, NOW, START, TOKEN, fixture_record, page, run, search_request


@pytest.mark.parametrize("empty", [False, True])
@freeze_time(NOW)
def test_issues_search_pagination(empty):
    first = fixture_record("issues")
    second = {**first, "id": "synthetic-second-issue"}
    with HttpMocker() as mocker:
        initial = search_request()
        mocker.post(initial, page([] if empty else [first], None if empty else "next"))
        if not empty:
            following = search_request(cursor="next")
            mocker.post(following, page([second]))
        output = run("issues", mode=SyncMode.incremental)
        mocker.assert_number_of_calls(initial, 1)
        if not empty:
            mocker.assert_number_of_calls(following, 1)
    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ([] if empty else [first["id"], second["id"]])


def test_two_pass_incremental():
    issue = fixture_record("issues")
    with freeze_time(NOW), HttpMocker() as mocker:
        mocker.post(search_request(), page([issue]))
        first = run("issues", mode=SyncMode.incremental)
    assert first.errors == []
    cursor = first.most_recent_state.stream_state.__dict__["updated_at"]
    edited = {**issue, "updated_at": "2026-01-15T12:00:00Z"}
    with freeze_time("2026-01-16T00:00:00Z"), HttpMocker() as mocker:
        request = search_request(start=cursor, end="2026-01-16T00:00:01Z")
        mocker.post(request, page([edited]))
        second = run("issues", mode=SyncMode.incremental, state=[message.state for message in first.state_messages])
        mocker.assert_number_of_calls(request, 1)
    assert second.errors == []
    assert [message.record.data["updated_at"] for message in second.records] == [edited["updated_at"]]


@freeze_time(NOW)
def test_legacy_state_rewinds_to_start_date():
    state = StateBuilder().with_stream_state("issues", {"created_at": "2026-01-12T00:00:00Z"}).build()
    with HttpMocker() as mocker:
        request = search_request()
        mocker.post(request, page([fixture_record("issues")]))
        output = run("issues", mode=SyncMode.incremental, state=state)
        mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    assert "updated_at" in output.most_recent_state.stream_state.__dict__
    assert "created_at" not in output.most_recent_state.stream_state.__dict__


@freeze_time("2026-02-01T00:00:00Z")
def test_thirty_day_windows_overlap_without_subsecond_gaps(requests_mock):
    edge = datetime(2026, 1, 31, tzinfo=timezone.utc)
    timestamps = [(edge + timedelta(seconds=offset)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") for offset in (-2, -1, -0.5, 0, 0.5, 1)]
    records = [{**fixture_record("issues"), "id": f"seam-{index}", "updated_at": stamp} for index, stamp in enumerate(timestamps)]
    windows = []

    def respond(request, context):
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        body = request.json()
        assert body["limit"] == 999
        time_filter = body["filter"]
        assert time_filter["operator"] == "time_range"
        start, end = time_filter["values"]
        selected = [
            record
            for record in records
            if datetime.fromisoformat(start) <= datetime.fromisoformat(record["updated_at"]) <= datetime.fromisoformat(end)
        ]
        windows.append((start, end))
        return {"data": selected, "pagination": {"has_next_page": False}}

    requests_mock.post(f"{BASE}/issues/search", json=respond)
    output = run("issues", cfg={**CONFIG, "start_date": START}, mode=SyncMode.incremental)
    assert output.errors == []
    assert requests_mock.call_count == 2
    emitted = {message.record.data["updated_at"] for message in output.records}
    assert emitted == set(timestamps), f"Lost whole seconds at the 30-day seam: {sorted(set(timestamps) - emitted)}"
    assert sorted(windows) == [
        (START, "2026-01-31T00:00:00Z"),
        ("2026-01-31T00:00:00Z", "2026-02-01T00:00:01Z"),
    ]
    first, second = sorted(windows)
    assert first[1] == second[0]
    assert all(datetime.fromisoformat(end) - datetime.fromisoformat(start) <= timedelta(days=30) for start, end in windows)
    counts = Counter(message.record.data["id"] for message in output.records)
    expected = Counter(record["id"] for record in records)
    expected["seam-3"] += 1
    assert counts == expected
    cursor = output.most_recent_state.stream_state.__dict__["updated_at"]
    assert datetime.fromisoformat(cursor) == max(datetime.fromisoformat(stamp) for stamp in timestamps)
    print(f"Seam windows: {sorted(windows)}")
    print(f"Subsecond seam record 2026-01-30T23:59:59.500000Z: {counts['seam-2']} emission; shared edge: {counts['seam-3']} emissions")
    print(f"Seam final cursor: {cursor}; unique IDs: {len(counts)}; emitted records: {sum(counts.values())}")


@freeze_time("2026-02-01T00:00:00Z")
def test_interrupted_read_resumes_from_last_emitted_state(requests_mock):
    checkpoint = "2026-01-31T00:00:00Z"
    end = "2026-02-01T00:00:00Z"
    records = [
        {**fixture_record("issues"), "id": identifier, "updated_at": stamp}
        for identifier, stamp in (
            ("resume-before", "2026-01-30T23:59:58Z"),
            ("resume-subsecond", "2026-01-30T23:59:59.500000Z"),
            ("resume-checkpoint", checkpoint),
            ("resume-after", "2026-01-31T00:00:00.500000Z"),
            ("resume-final", end),
        )
    ]
    windows = []
    interrupted = True

    def respond(request, context):
        time_filter = request.json()["filter"]
        assert time_filter["operator"] == "time_range"
        start, stop = time_filter["values"]
        windows.append((start, stop))
        if interrupted and start == checkpoint:
            context.status_code = 400
            return {"code": "invalid_request_body", "errors": ["Synthetic interrupted window"]}
        return {
            "data": [
                record
                for record in records
                if datetime.fromisoformat(start) <= datetime.fromisoformat(record["updated_at"]) <= datetime.fromisoformat(stop)
            ]
        }

    requests_mock.post(f"{BASE}/issues/search", json=respond)
    config = {**CONFIG, "num_workers": 2}
    first_window_complete = Event()
    process_partition = PartitionReader.process_partition

    def process_in_order(reader, partition, cursor):
        start = partition.to_slice()["start_time"]
        if start != START:
            assert first_window_complete.wait(timeout=5)
        process_partition(reader, partition, cursor)
        if start == START:
            first_window_complete.set()

    with patch.object(PartitionReader, "process_partition", process_in_order):
        first = run("issues", cfg=config, mode=SyncMode.incremental, expecting_exception=True)
    assert first.errors
    assert first.state_messages
    messages = list(first.get_message_iterator())
    assert next(index for index, message in enumerate(messages) if message.state) < next(
        index for index, message in enumerate(messages) if message.trace and message.trace.error
    )
    assert first.most_recent_state.stream_state.__dict__["updated_at"] == checkpoint
    assert windows == [(START, checkpoint), ("2026-01-31T00:00:00Z", "2026-02-01T00:00:01Z")]
    assert [message.record.data["id"] for message in first.records] == ["resume-before", "resume-subsecond", "resume-checkpoint"]
    assert datetime.fromisoformat(checkpoint) == max(datetime.fromisoformat(message.record.data["updated_at"]) for message in first.records)

    windows.clear()
    interrupted = False
    resumed = run("issues", cfg=config, mode=SyncMode.incremental, state=[first.state_messages[-1].state])
    assert resumed.errors == []
    assert windows == [(checkpoint, "2026-02-01T00:00:01Z")]
    assert [message.record.data["id"] for message in resumed.records] == ["resume-checkpoint", "resume-after", "resume-final"]
    combined = Counter(message.record.data["id"] for output in (first, resumed) for message in output.records)
    assert combined == Counter({"resume-before": 1, "resume-subsecond": 1, "resume-checkpoint": 2, "resume-after": 1, "resume-final": 1})
    assert set(combined) == {record["id"] for record in records}
    assert resumed.most_recent_state.stream_state.__dict__["updated_at"] == end
    print(f"Resume checkpoint: {checkpoint}; final cursor: {end}; ID multiplicities: {dict(combined)}")


@pytest.mark.parametrize("start", ["2026-01-14T23:59:59Z", NOW, "2025-12-16T00:00:00Z"])
@freeze_time(NOW)
def test_final_issue_window_extends_one_second_with_thirty_day_clamp(requests_mock, start):
    records = [
        {**fixture_record("issues"), "id": "at-now", "updated_at": NOW},
        {**fixture_record("issues"), "id": "after-now", "updated_at": "2026-01-15T00:00:00.500000Z"},
    ]
    windows = []

    def respond(request, context):
        lower, upper = request.json()["filter"]["values"]
        windows.append((lower, upper))
        return {
            "data": [
                record
                for record in records
                if datetime.fromisoformat(lower) <= datetime.fromisoformat(record["updated_at"]) <= datetime.fromisoformat(upper)
            ]
        }

    requests_mock.post(f"{BASE}/issues/search", json=respond)
    output = run("issues", cfg={**CONFIG, "start_date": start}, mode=SyncMode.incremental)
    assert output.errors == []
    clamped = start == "2025-12-16T00:00:00Z"
    upper = NOW if clamped else "2026-01-15T00:00:01Z"
    assert windows == [(start, upper)]
    assert [message.record.data["id"] for message in output.records] == (["at-now"] if clamped else ["at-now", "after-now"])
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == NOW
    print(f"Final window: {windows[0]}; cursor: {NOW}")


def test_final_issue_window_filter_is_stable_across_pages(requests_mock) -> None:
    filters = []
    records = [{**fixture_record("issues"), "id": f"final-page-{index}"} for index in range(3)]
    with freeze_time(NOW) as clock:

        def respond(request, context):
            body = request.json()
            index = len(filters)
            assert body.get("cursor") == (None if index == 0 else f"page-{index}")
            filters.append(body["filter"])
            clock.tick(delta=timedelta(seconds=5))
            return {
                "data": [records[index]],
                "pagination": {"has_next_page": index < 2, "cursor": f"page-{index + 1}"},
            }

        requests_mock.post(f"{BASE}/issues/search", json=respond)
        output = run("issues", mode=SyncMode.incremental)
    assert output.errors == []
    assert requests_mock.call_count == 3
    assert filters == [{"field": "updated_at", "operator": "time_range", "values": [START, "2026-01-15T00:00:01Z"]}] * 3
    assert [message.record.data["id"] for message in output.records] == [record["id"] for record in records]
