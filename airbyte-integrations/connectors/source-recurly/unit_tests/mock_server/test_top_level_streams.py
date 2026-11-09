# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.helpers import NOW, START, list_request, page, page_request, record, run


STREAMS = ("add_ons", "credit_payments", "plans", "shipping_methods")


@pytest.mark.parametrize("stream", STREAMS)
@freeze_time(NOW)
def test_full_refresh_follows_next_link_across_pages(stream):
    with HttpMocker() as mocker:
        mocker.get(
            list_request(stream),
            page([record(f"{stream}-1", "2026-01-02T00:00:00Z")], next_path=f"/{stream}?cursor=page-2&limit=200"),
        )
        mocker.get(page_request(stream, "page-2"), page([record(f"{stream}-2", "2026-01-03T00:00:00Z")]))
        output = run(stream)
    assert [message.record.data["id"] for message in output.records] == [f"{stream}-1", f"{stream}-2"]
    assert output.errors == []


@pytest.mark.parametrize("stream", STREAMS)
@freeze_time(NOW)
def test_empty_page_emits_no_records(stream):
    with HttpMocker() as mocker:
        request = list_request(stream)
        mocker.get(request, page([]))
        output = run(stream)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    assert output.errors == []


@pytest.mark.parametrize("stream", STREAMS)
@freeze_time(NOW)
def test_incremental_without_state_starts_at_begin_time_and_emits_latest_cursor(stream):
    with HttpMocker() as mocker:
        mocker.get(
            list_request(stream, begin=START),
            page([record(f"{stream}-1", "2026-01-04T00:00:00Z"), record(f"{stream}-2", "2026-01-09T12:00:00Z")]),
        )
        output = run(stream, mode=SyncMode.incremental)
    assert [message.record.data["id"] for message in output.records] == [f"{stream}-1", f"{stream}-2"]
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-01-09T12:00:00Z"


@pytest.mark.parametrize("stream", STREAMS)
@freeze_time(NOW)
def test_incremental_with_state_resumes_from_saved_cursor(stream):
    state = StateBuilder().with_stream_state(stream, {"updated_at": "2026-01-10T00:00:00Z"}).build()
    with HttpMocker() as mocker:
        request = list_request(stream, begin="2026-01-10T00:00:00Z")
        mocker.get(request, page([record(f"{stream}-3", "2026-01-12T00:00:00Z")]))
        output = run(stream, mode=SyncMode.incremental, state=state)
        mocker.assert_number_of_calls(request, 1)
    assert [message.record.data["id"] for message in output.records] == [f"{stream}-3"]
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-01-12T00:00:00Z"
