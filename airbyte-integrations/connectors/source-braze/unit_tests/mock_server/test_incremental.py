# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStreamStatus, Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker
        mocker._validate_all_matchers_called()


@pytest.mark.parametrize("empty", [False, True])
@pytest.mark.parametrize(
    "stream, path, field",
    [
        ("kpi_daily_new_users", "new_users", "new_users"),
        ("kpi_daily_active_users", "dau", "dau"),
        ("kpi_daily_app_uninstalls", "uninstalls", "uninstalls"),
    ],
)
@freeze_time("2026-04-13")
def test_incremental_windows(source_builder, empty: bool, stream: str, path: str, field: str, http_mocker: HttpMocker) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    records = []
    for ending_at, length in [("2026-04-10", "100"), ("2026-04-13", "3")]:
        data = [] if empty else [{"time": ending_at, field: 2}]
        records.extend(data)
        http_mocker.get(
            HttpRequest(
                f"https://rest.example.com/kpi/{path}/data_series",
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
                f"https://rest.example.com/kpi/{path}/data_series",
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


@pytest.mark.parametrize("empty", [False, True])
@freeze_time("2026-01-03")
def test_events_analytics_state(source_builder, http_mocker: HttpMocker, empty: bool) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream("events_analytics", SyncMode.incremental).build()
    http_mocker.get(HttpRequest("https://rest.example.com/events/list"), HttpResponse(json.dumps({"events": ["e1"]})))
    data = [] if empty else [{"time": "2026-01-03", "count": 5}]
    http_mocker.get(
        HttpRequest(
            "https://rest.example.com/events/data_series",
            query_params={"event": "e1", "unit": "day", "length": "3", "ending_at": "2026-01-03"},
        ),
        HttpResponse(json.dumps({"data": data, "message": "success"})),
    )
    output = read(source_builder(config=config, catalog=catalog), config, catalog)
    assert not output.errors
    assert [message.record.data for message in output.records] == [dict(record, event_id="e1") for record in data]
    state = output.most_recent_state.stream_state.__dict__
    assert state["states"] == [
        {"partition": {"event": "e1", "parent_slice": {}}, "cursor": {"time": "2026-01-01" if empty else "2026-01-03"}}
    ]


@pytest.mark.parametrize(
    "stream, endpoint, page_size",
    [("campaigns", "campaigns", 100), ("canvases", "canvas", 100), ("segments", "segments", 100), ("events", "events", 250)],
)
@pytest.mark.parametrize("full_page", [False, True])
def test_list_pagination(source_builder, http_mocker: HttpMocker, stream: str, endpoint: str, page_size: int, full_page: bool) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    size = page_size if full_page else 3
    records = [
        f"event-{i}" if stream == "events" else {"id": str(i), "last_edited": "2026-01-02T00:00:00+00:00"}
        for i in range(size + int(full_page))
    ]
    params = {}
    if stream != "events":
        params["last_edit.time[gt]"] = "2026-01-01T00:00:00" if stream in ["campaigns", "canvases"] else "2026-01-01"
    if stream in ["campaigns", "canvases"]:
        params["include_archived"] = "true"
    first = HttpRequest(f"https://rest.example.com/{endpoint}/list", query_params=params)
    http_mocker.get(first, HttpResponse(json.dumps({stream: records[:size]})))
    if full_page:
        second = HttpRequest(f"https://rest.example.com/{endpoint}/list", query_params=dict(params, page="1"))
        http_mocker.get(second, HttpResponse(json.dumps({stream: records[size:]})))
    output = read(source_builder(config=config, catalog=catalog), config, catalog)
    assert not output.errors
    expected = [{"event_name": record} for record in records] if stream == "events" else records
    assert [message.record.data for message in output.records] == expected
    http_mocker.assert_number_of_calls(first, 1)
    if full_page:
        http_mocker.assert_number_of_calls(second, 1)
    assert len(http_mocker._mocker.request_history) == (2 if full_page else 1)
    assert output.get_stream_statuses(stream)[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize("stream, parent_missing", [("cards", True), ("cards_analytics", True), ("cards_analytics", False)])
@freeze_time("2026-01-03")
def test_retired_feed_completes(source_builder, http_mocker: HttpMocker, stream: str, parent_missing: bool) -> None:
    config = {"url": "https://rest.example.com", "api_key": "test-key", "start_date": "2026-01-01"}
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental if stream == "cards_analytics" else SyncMode.full_refresh).build()
    parent = HttpRequest("https://rest.example.com/feed/list", query_params={"last_edit.time[gt]": "2026-01-01"})
    http_mocker.get(
        parent,
        HttpResponse(json.dumps({"message": "Invalid URL"}), status_code=404)
        if parent_missing
        else HttpResponse(json.dumps({"cards": [{"id": "c1"}]})),
    )
    if not parent_missing:
        analytics = HttpRequest(
            "https://rest.example.com/feed/data_series",
            query_params={"card_id": "c1", "length": "3", "ending_at": "2026-01-03"},
        )
        http_mocker.get(analytics, HttpResponse(json.dumps({"message": "Invalid URL"}), status_code=404))
    output = read(source_builder(config=config, catalog=catalog), config, catalog)
    assert not output.errors
    assert not output.records
    assert not [message for message in output.logs if message.log.level == Level.ERROR]
    assert output.get_stream_statuses(stream)[-1] == AirbyteStreamStatus.COMPLETE
    http_mocker.assert_number_of_calls(parent, 1)
    if not parent_missing:
        http_mocker.assert_number_of_calls(analytics, 1)
