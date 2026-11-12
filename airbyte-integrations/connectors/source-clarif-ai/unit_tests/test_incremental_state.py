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
    "start_date": "2026-01-01T00:00:00Z",
}
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
_APPS = [
    {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
    {"id": "app3", "modified_at": "2026-03-05T06:07:08Z"},
    {"id": "app4", "modified_at": "2026-04-05T06:07:08.123456Z"},
    {"id": "app5"},
]
# Clarifai returns nanosecond precision; state is stored with microsecond precision.
_CHILD_RECORDS = {
    "app3": [],
    "app4": [],
    "app5": [],
    "app1": [
        {"id": "app1_old", "modified_at": "2026-09-30T08:00:00.123456789Z"},
        {"id": "app1_new", "modified_at": "2026-10-20T11:22:33.987654321Z"},
    ],
    "app2": [{"id": "app2_only", "modified_at": "2026-11-01T01:02:03.000000001Z"}],
}
_EXPECTED_CHILD_CURSORS = {
    "app3": "2026-01-01T00:00:00.000000Z",
    "app4": "2026-01-01T00:00:00.000000Z",
    "app5": "2026-01-01T00:00:00.000000Z",
    "app1": "2026-10-20T11:22:33.987654Z",
    "app2": "2026-11-01T01:02:03.000000Z",
}


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _mock_api(mocker, child_path=None):
    mocker.get(_BASE_URL, json={"apps": _APPS})
    for app_id, records in _CHILD_RECORDS.items():
        if child_path:
            mocker.get(f"{_BASE_URL}/{app_id}/{child_path}", json={child_path: records})


def test_applications_state_advances_to_newest_modified_at():
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        first_read = _read("applications")

        assert first_read.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}
        # Values beyond microsecond precision are truncated so the cursor can parse them; others are untouched.
        assert {record.record.data["id"]: record.record.data.get("modified_at") for record in first_read.records} == {
            "app1": "2026-10-02T17:05:11.904417Z",
            "app2": "2026-10-14T09:41:55.568082Z",
            "app3": "2026-03-05T06:07:08Z",
            "app4": "2026-04-05T06:07:08.123456Z",
            "app5": None,
        }

        state = StateBuilder().with_stream_state("applications", first_read.most_recent_state.stream_state.__dict__).build()
        second_read = _read("applications", state)

    # The stream has no server-side or client-side filter, so every record is read again and the state is carried forward.
    assert [record.record.data["id"] for record in second_read.records] == ["app1", "app2", "app3", "app4", "app5"]
    assert second_read.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_state_advances_per_app_partition(stream_name):
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker, child_path=stream_name)
        first_read = _read(stream_name)

        assert [record.record.data["id"] for record in first_read.records] == ["app1_old", "app1_new", "app2_only"]
        first_state = first_read.most_recent_state.stream_state.__dict__
        assert {
            partition["partition"]["app_id"]: partition["cursor"]["modified_at"] for partition in first_state["states"]
        } == _EXPECTED_CHILD_CURSORS

        state = StateBuilder().with_stream_state(stream_name, first_state).build()
        second_read = _read(stream_name, state)

    assert [record.record.data["id"] for record in second_read.records] == ["app1_old", "app1_new", "app2_only"]
    second_state = second_read.most_recent_state.stream_state.__dict__
    assert {
        partition["partition"]["app_id"]: partition["cursor"]["modified_at"] for partition in second_state["states"]
    } == _EXPECTED_CHILD_CURSORS
