# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.helpers import BASE, CONFIG, NOW, START, TOKEN, fixture_record, page, run, search_request


@pytest.mark.parametrize("empty", [False, True])
@freeze_time(NOW)
def test_issues_search_pagination(empty):
    first = fixture_record("issues")
    second = {**first, "id": "synthetic-second-issue"}
    with HttpMocker() as mocker:
        initial = search_request(exclusive=True)
        mocker.post(initial, page([] if empty else [first], None if empty else "next"))
        if not empty:
            following = search_request(cursor="next", exclusive=True)
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
        mocker.post(search_request(exclusive=True), page([issue]))
        first = run("issues", mode=SyncMode.incremental)
    assert first.errors == []
    cursor = first.most_recent_state.stream_state.__dict__["updated_at"]
    edited = {**issue, "updated_at": "2026-01-15T12:00:00Z"}
    with freeze_time("2026-01-16T00:00:00Z"), HttpMocker() as mocker:
        request = search_request(start=cursor, end="2026-01-16T00:00:00Z", exclusive=True)
        mocker.post(request, page([edited]))
        second = run("issues", mode=SyncMode.incremental, state=[message.state for message in first.state_messages])
        mocker.assert_number_of_calls(request, 1)
    assert second.errors == []
    assert [message.record.data["updated_at"] for message in second.records] == [edited["updated_at"]]


@freeze_time(NOW)
def test_legacy_state_rewinds_to_start_date():
    state = StateBuilder().with_stream_state("issues", {"created_at": "2026-01-12T00:00:00Z"}).build()
    with HttpMocker() as mocker:
        request = search_request(exclusive=True)
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

    def respond(request, context):
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        body = request.json()
        assert body["limit"] == 999
        time_filter = body["filter"]
        if time_filter["operator"] == "time_range":
            start, end = time_filter["values"]
            selected = [record for record in records if start <= record["updated_at"] <= end]
        else:
            start, end = [item["value"] for item in time_filter["subfilters"]]
            selected = [record for record in records if start < record["updated_at"] < end]
        return {"data": selected, "pagination": {"has_next_page": False}}

    requests_mock.post(f"{BASE}/issues/search", json=respond)
    output = run("issues", cfg={**CONFIG, "start_date": START}, mode=SyncMode.incremental)
    assert output.errors == []
    assert requests_mock.call_count == 2
    emitted = {message.record.data["updated_at"] for message in output.records}
    assert emitted == set(timestamps), f"Lost whole seconds at the 30-day seam: {sorted(set(timestamps) - emitted)}"
