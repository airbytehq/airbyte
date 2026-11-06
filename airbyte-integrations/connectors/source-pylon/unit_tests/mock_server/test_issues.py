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
        request = search_request(start=cursor, end="2026-01-16T00:00:00Z")
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
def test_thirty_day_window_seam_loses_no_seconds(requests_mock):
    edge = datetime(2026, 1, 31, tzinfo=timezone.utc)
    timestamps = [(edge + timedelta(seconds=offset)).strftime("%Y-%m-%dT%H:%M:%SZ") for offset in (-2, -1, 0, 1)]
    records = [{**fixture_record("issues"), "id": f"seam-{index}", "updated_at": stamp} for index, stamp in enumerate(timestamps)]
    windows = []

    def respond(request, context):
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        body = request.json()
        assert body["limit"] == 999
        time_filter = body["filter"]
        assert time_filter["operator"] == "time_range"
        start, end = time_filter["values"]
        selected = [record for record in records if start <= record["updated_at"] <= end]
        windows.append((start, end))
        return {"data": selected, "pagination": {"has_next_page": False}}

    requests_mock.post(f"{BASE}/issues/search", json=respond)
    output = run("issues", cfg={**CONFIG, "start_date": START}, mode=SyncMode.incremental)
    assert output.errors == []
    assert requests_mock.call_count == 2
    emitted = {message.record.data["updated_at"] for message in output.records}
    assert emitted == set(timestamps), f"Lost whole seconds at the 30-day seam: {sorted(set(timestamps) - emitted)}"
    assert sorted(windows) == [
        (START, "2026-01-30T23:59:59Z"),
        ("2026-01-31T00:00:00Z", "2026-02-01T00:00:00Z"),
    ]
    first, second = sorted(windows)
    assert datetime.fromisoformat(second[0]) - datetime.fromisoformat(first[1]) == timedelta(seconds=1)
    assert Counter(message.record.data["id"] for message in output.records) == Counter(record["id"] for record in records)


@freeze_time("2026-02-01T00:00:00Z")
def test_interrupted_read_resumes_from_last_emitted_state(requests_mock):
    checkpoint = "2026-01-30T23:59:59Z"
    end = "2026-02-01T00:00:00Z"
    records = [
        {**fixture_record("issues"), "id": identifier, "updated_at": stamp}
        for identifier, stamp in (
            ("resume-before", "2026-01-30T23:59:58Z"),
            ("resume-checkpoint", checkpoint),
            ("resume-after", "2026-01-31T00:00:00Z"),
            ("resume-final", end),
        )
    ]
    windows = []

    def respond(request, context):
        time_filter = request.json()["filter"]
        assert time_filter["operator"] == "time_range"
        start, stop = time_filter["values"]
        windows.append((start, stop))
        if start == "2026-01-31T00:00:00Z":
            context.status_code = 400
            return {"code": "invalid_request_body", "errors": ["Synthetic interrupted window"]}
        return {"data": [record for record in records if start <= record["updated_at"] <= stop]}

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
    assert windows == [(START, checkpoint), ("2026-01-31T00:00:00Z", end)]
    assert [message.record.data["id"] for message in first.records] == ["resume-before", "resume-checkpoint"]

    windows.clear()
    resumed = run("issues", cfg=config, mode=SyncMode.incremental, state=[first.state_messages[-1].state])
    assert resumed.errors == []
    assert windows == [(checkpoint, end)]
    assert [message.record.data["id"] for message in resumed.records] == ["resume-checkpoint", "resume-after", "resume-final"]
    combined = Counter(message.record.data["id"] for output in (first, resumed) for message in output.records)
    assert combined == Counter({"resume-before": 1, "resume-checkpoint": 2, "resume-after": 1, "resume-final": 1})
    assert set(combined) == {record["id"] for record in records}
    assert resumed.most_recent_state.stream_state.__dict__["updated_at"] == end
