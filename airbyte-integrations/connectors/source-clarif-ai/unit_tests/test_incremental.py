# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2024-01-01T00:00:00Z",
}
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("fraction", ["904417302", "904417"])
def test_incremental_state_advances(stream_name, fraction):
    records = [
        {"id": "missing"},
        {"id": "null", "modified_at": None},
        {"id": "milliseconds", "modified_at": "2024-01-02T17:05:10.123Z"},
        {"id": "older", "modified_at": "2024-01-02T17:05:11.123456Z"},
        {"id": "newest", "modified_at": f"2024-01-03T17:05:11.{fraction}Z"},
    ]
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        if stream_name == "applications":
            mocker.get(_BASE_URL, json={"apps": records})
        else:
            mocker.get(_BASE_URL, json={"apps": [{"id": "app1", "modified_at": "2024-01-02T17:05:11.123456Z"}]})
            mocker.get(f"{_BASE_URL}/app1/{stream_name}", json={stream_name: records})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    state = vars(output.most_recent_state.stream_state)
    cursor = state if stream_name == "applications" else state["state"]
    assert cursor == {"modified_at": "2024-01-03T17:05:11.904417Z"}
    if stream_name != "applications":
        assert state["states"] == [
            {"partition": {"app_id": "app1", "parent_slice": {}}, "cursor": cursor}
        ]
    assert not output.errors
    expected_records = [dict(record) for record in records]
    expected_records[1] = {"id": "null"}
    expected_records[-1]["modified_at"] = "2024-01-03T17:05:11.904417Z"
    assert [message.record.data for message in output.records] == expected_records

    emitted_state = StateBuilder().with_stream_state(stream_name, state).build()
    with requests_mock.Mocker() as mocker:
        if stream_name == "applications":
            mocker.get(_BASE_URL, json={"apps": []})
        else:
            mocker.get(_BASE_URL, json={"apps": [{"id": "app1", "modified_at": "2024-01-02T17:05:11.123456Z"}]})
            mocker.get(f"{_BASE_URL}/app1/{stream_name}", json={stream_name: []})
        resumed = read(get_source(_CONFIG, state=emitted_state), config=_CONFIG, catalog=catalog, state=emitted_state)

    assert not resumed.errors
    assert resumed.records == []
    resumed_state = vars(resumed.most_recent_state.stream_state)
    if stream_name == "applications":
        assert resumed_state == cursor
    else:
        assert resumed_state["state"] == cursor
        assert resumed_state["states"] == state["states"]
