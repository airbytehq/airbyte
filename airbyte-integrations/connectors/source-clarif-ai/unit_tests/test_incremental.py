# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


def _expected_state(stream_name, timestamp):
    cursor = {"modified_at": timestamp}
    if stream_name == "applications":
        return cursor
    return {
        "use_global_cursor": False,
        "states": [{"partition": {"app_id": "app1", "parent_slice": {}}, "cursor": cursor}],
        "state": cursor,
        "lookback_window": 1,
        "parent_state": {},
    }


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_nanosecond_cursor_advances_and_resumes(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    field = "apps" if stream_name == "applications" else stream_name
    url = _APPS_URL if stream_name == "applications" else f"{_APPS_URL}/app1/{stream_name}"
    records = [
        {"id": "short", "modified_at": "2026-09-01T00:00:00.123Z"},
        {"id": "old", "modified_at": "2026-10-01T00:00:00.123456Z"},
        {"id": "first", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "latest", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        {"id": "null", "modified_at": None},
        {"id": "missing"},
    ]

    with requests_mock.Mocker() as mocker:
        if stream_name != "applications":
            mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-01T00:00:00.123456Z"}]})
        mocker.get(url, json={field: records})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert [message.record.data["id"] for message in output.records] == ["short", "old", "first", "latest", "null", "missing"]
    assert output.errors == []
    state = vars(output.most_recent_state.stream_state)
    assert state == _expected_state(stream_name, "2026-10-14T09:41:55.568082Z")
    expected_records = [
        {"id": "short", "modified_at": "2026-09-01T00:00:00.123Z"},
        {"id": "old", "modified_at": "2026-10-01T00:00:00.123456Z"},
        {"id": "first", "modified_at": "2026-10-02T17:05:11.904417Z"},
        {"id": "latest", "modified_at": "2026-10-14T09:41:55.568082Z"},
        {"id": "null"},
        {"id": "missing"},
    ]
    assert [message.record.data for message in output.records] == expected_records

    with requests_mock.Mocker() as mocker:
        if stream_name != "applications":
            mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-01T00:00:00.123456Z"}]})
        response = mocker.get(url, json={field: records})
        emitted_state = [output.state_messages[-1].state]
        resumed = read(get_source(_CONFIG, state=emitted_state), config=_CONFIG, catalog=catalog, state=emitted_state)

    assert response.last_request.qs == {"page": ["1"], "per_page": ["20" if stream_name == "applications" else "100"]}
    assert response.call_count == 1
    assert resumed.errors == []
    assert [message.record.data for message in resumed.records] == expected_records
    assert vars(resumed.most_recent_state.stream_state) == state
