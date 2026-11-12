# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import date, timedelta

from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import BambooHrRequestBuilder
from mock_server.response_builder import response


@freeze_time("2026-11-10T00:00:00Z")
def test_nullable_and_offset_entries(http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    request = (
        BambooHrRequestBuilder("time_tracking/timesheet_entries")
        .with_query_param("start", "2026-11-01")
        .with_query_param("end", "2026-11-10")
        .build()
    )
    http_mocker.get(
        request,
        response(
            [
                {"id": 1, "start": None, "end": None, "hours": 4},
                {"id": 2, "start": "2026-11-05T09:00:00-06:00", "end": "2026-11-05T17:00:00-06:00"},
            ]
        ),
    )
    output = read(
        get_source(config),
        config,
        CatalogBuilder().with_stream("timesheet_entries", SyncMode.incremental).build(),
    )
    assert output.errors == []
    assert {message.record.data["id"] for message in output.records} == {1, 2}
    assert len(output.records) == 2
    assert output.state_messages
    assert output.most_recent_state.stream_state.start == "2026-11-05"
    http_mocker.assert_number_of_calls(request, 1)


@freeze_time("2026-11-10T00:00:00Z")
def test_saved_state_replays_30_days(http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().with_start_date("2026-10-01T00:00:00Z").build()
    catalog = CatalogBuilder().with_stream("timesheet_entries", SyncMode.incremental).build()
    initial = (
        BambooHrRequestBuilder("time_tracking/timesheet_entries")
        .with_query_param("start", "2026-10-01")
        .with_query_param("end", "2026-10-31")
        .build()
    )
    current = (
        BambooHrRequestBuilder("time_tracking/timesheet_entries")
        .with_query_param("start", "2026-11-01")
        .with_query_param("end", "2026-11-10")
        .build()
    )
    http_mocker.get(initial, response([]))
    http_mocker.get(current, response([{"id": 1, "start": "2026-11-05T09:00:00+00:00"}]))
    first = read(get_source(config), config, catalog)
    assert first.errors == []
    assert [message.record.data["id"] for message in first.records] == [1]
    assert first.most_recent_state.stream_state.start == "2026-11-05"
    state = [first.state_messages[-1].state]
    replay = (
        BambooHrRequestBuilder("time_tracking/timesheet_entries")
        .with_query_param("start", "2026-10-06")
        .with_query_param("end", "2026-11-05")
        .build()
    )
    http_mocker.get(
        replay,
        response([{"id": 2, "start": "2026-10-10T09:00:00+00:00"}, {"id": 1, "start": "2026-11-05T09:00:00+00:00"}]),
    )
    remaining = (
        BambooHrRequestBuilder("time_tracking/timesheet_entries")
        .with_query_param("start", "2026-11-06")
        .with_query_param("end", "2026-11-10")
        .build()
    )
    http_mocker.get(remaining, response([]))
    second = read(get_source(config, state), config, catalog, state=state)
    http_mocker.assert_number_of_calls(replay, 1)
    assert second.errors == []
    assert {message.record.data["id"] for message in second.records} == {1, 2}
    assert len(second.records) == 2
    assert second.most_recent_state.stream_state.start == "2026-11-05"
    http_mocker.assert_number_of_calls(initial, 1)
    http_mocker.assert_number_of_calls(current, 1)
    http_mocker.assert_number_of_calls(remaining, 1)


@freeze_time("2026-11-10T00:00:00Z")
def test_old_start_date_is_clamped(http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().with_start_date("2020-01-01T00:00:00Z").build()
    start = date(2025, 11, 11)
    requests = []
    while start <= date(2026, 11, 10):
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        end = min(next_month - timedelta(days=1), date(2026, 11, 10))
        request = (
            BambooHrRequestBuilder("time_tracking/timesheet_entries")
            .with_query_param("start", start.isoformat())
            .with_query_param("end", end.isoformat())
            .build()
        )
        http_mocker.get(request, response([]))
        requests.append(request)
        start = next_month
    output = read(
        get_source(config),
        config,
        CatalogBuilder().with_stream("timesheet_entries", SyncMode.incremental).build(),
    )
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    assert output.records == []
    assert output.state_messages
