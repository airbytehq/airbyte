# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_BASE = "https://api.clarifai.com/v2/users/test_user_id/apps"
_APPS = {"apps": [{"id": "app1", "modified_at": "2026-05-01T00:00:00.000000Z"}]}
_RECORDS = [
    {"id": "old", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    {"id": "new", "modified_at": "2026-10-14T09:41:55.568082659Z"},
]
_NEWEST = "2026-10-14T09:41:55.568082Z"


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with requests_mock.Mocker() as m:
        if stream_name == "applications":
            m.get(_BASE, json={"apps": _RECORDS})
        else:
            m.get(_BASE, json=_APPS)
            m.get(f"{_BASE}/app1/{stream_name}", json={stream_name: _RECORDS})
        return read(get_source(_CONFIG, state), _CONFIG, catalog, state)


def _final_cursor(output, stream_name):
    state = output.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        return state["modified_at"]
    return {s["partition"]["app_id"]: s["cursor"]["modified_at"] for s in state["states"]}


def _expected_cursor(stream_name, value):
    return value if stream_name == "applications" else {"app1": value}


def _state(stream_name, value):
    if stream_name == "applications":
        return StateBuilder().with_stream_state(stream_name, {"modified_at": value}).build()
    return (
        StateBuilder()
        .with_stream_state(
            stream_name,
            {"states": [{"partition": {"app_id": "app1", "parent_slice": {}}, "cursor": {"modified_at": value}}]},
        )
        .build()
    )


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_state_advances_to_newest_nanosecond_modified_at(stream_name):
    output = _read(stream_name)

    assert [r.record.data["id"] for r in output.records] == ["old", "new"]
    assert _final_cursor(output, stream_name) == _expected_cursor(stream_name, _NEWEST)


@pytest.mark.parametrize(
    "incoming_cursor,expected_cursor",
    [
        pytest.param("2026-10-10T00:00:00.000000Z", _NEWEST, id="newer_records_advance_state"),
        pytest.param("2026-11-01T00:00:00.000000Z", "2026-11-01T00:00:00.000000Z", id="state_carried_forward"),
    ],
)
@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_next_sync_carries_state_forward(stream_name, incoming_cursor, expected_cursor):
    output = _read(stream_name, _state(stream_name, incoming_cursor))

    assert _final_cursor(output, stream_name) == _expected_cursor(stream_name, expected_cursor)
