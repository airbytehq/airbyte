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
