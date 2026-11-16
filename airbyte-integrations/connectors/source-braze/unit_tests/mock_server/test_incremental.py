# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker
        mocker._validate_all_matchers_called()


@pytest.mark.parametrize("empty", [False, True])
@freeze_time("2026-04-13")
def test_incremental_windows(source_builder, empty: bool, http_mocker: HttpMocker) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream("kpi_daily_new_users", SyncMode.incremental).build()
    records = []
    for ending_at, length in [("2026-04-10", "100"), ("2026-04-13", "3")]:
        data = [] if empty else [{"time": ending_at, "new_users": 2}]
        records.extend(data)
        http_mocker.get(
            HttpRequest(
                "https://rest.example.com/kpi/new_users/data_series",
                query_params={"ending_at": ending_at, "length": length},
            ),
            HttpResponse(json.dumps({"data": data})),
        )
    output = read(source_builder(config=config, catalog=catalog), config, catalog)
    assert not output.errors
    assert sorted((message.record.data for message in output.records), key=lambda record: record["time"]) == records
    assert output.most_recent_state.stream_state.__dict__ == {"time": "2026-01-01" if empty else "2026-04-13"}
    if not empty:
        state = [message.state for message in output.state_messages[-1:]]
        http_mocker.get(
            HttpRequest(
                "https://rest.example.com/kpi/new_users/data_series",
                query_params={"ending_at": "2026-04-13", "length": "1"},
            ),
            HttpResponse(json.dumps({"data": [records[-1]]})),
        )
        resumed = read(source_builder(config=config, catalog=catalog, state=state), config, catalog, state)
        assert [message.record.data for message in resumed.records] == [records[-1]]
        assert resumed.most_recent_state.stream_state.__dict__ == {"time": "2026-04-13"}


@pytest.mark.parametrize("events", [["purchase"], []])
def test_events_extractor(source_builder, events: list[str], http_mocker: HttpMocker) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    http_mocker.get(
        HttpRequest("https://rest.example.com/events/list"),
        HttpResponse(json.dumps({"events": events})),
    )
    output = read(source_builder(config=config, catalog=catalog), config, catalog)
    assert not output.errors
    assert [message.record.data for message in output.records] == [{"event_name": event} for event in events]


@pytest.mark.parametrize("stream, endpoint", [("campaigns", "campaigns"), ("canvases", "canvas")])
@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
@pytest.mark.parametrize("edited_at", ["2026-01-02T12:34:56+00:00", "2026-01-02T12:34:56.123Z", None])
def test_list_last_edited_cursor(
    source_builder, http_mocker: HttpMocker, stream: str, endpoint: str, sync_mode: SyncMode, edited_at: str | None
) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    records = [{"id": "older", "last_edited": "2026-01-01T10:00:00+00:00"}, {"id": "one", "last_edited": edited_at}] if edited_at else []
    http_mocker.get(
        HttpRequest(
            f"https://rest.example.com/{endpoint}/list",
            query_params={"include_archived": "true", "last_edit.time[gt]": "2026-01-01T00:00:00"},
        ),
        HttpResponse(json.dumps({stream: records})),
    )
    output = read(source_builder(config=config, catalog=catalog), config, catalog)
    assert not output.errors
    assert [message.record.data for message in output.records] == records
    if sync_mode == SyncMode.incremental:
        cursor = "2026-01-02T12:34:56" if edited_at else "2026-01-01T00:00:00"
        assert output.most_recent_state.stream_state.__dict__ == {"last_edited": cursor}
        if not edited_at:
            return
        state = [message.state for message in output.state_messages[-1:]]
        http_mocker.get(
            HttpRequest(
                f"https://rest.example.com/{endpoint}/list",
                query_params={"include_archived": "true", "last_edit.time[gt]": cursor},
            ),
            HttpResponse(json.dumps({stream: [records[-1]]})),
        )
        resumed = read(source_builder(config=config, catalog=catalog, state=state), config, catalog, state)
        assert not resumed.errors
        assert [message.record.data for message in resumed.records] == [records[-1]]
        assert resumed.most_recent_state.stream_state.__dict__ == {"last_edited": cursor}
