# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re

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
_START_STATE = "2026-01-01T00:00:00.000000Z"
_APPS_URL = re.compile(r"^https://api\.clarifai\.com/v2/users/test_user_id/apps(\?.*)?$")


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def test_applications_state_advances_past_nanosecond_modified_at_and_is_carried_forward():
    first_page = {
        "apps": [
            {"id": "app_old", "modified_at": "2026-10-02T17:05:11.904417302Z"},
            {"id": "app_new", "modified_at": "2026-10-14T09:41:55.568082659Z"},
            {"id": "app_whole_seconds", "modified_at": "2026-10-10T08:00:00Z"},
        ]
    }
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json=first_page)
        first = _read("applications")

    assert [r.record.data["id"] for r in first.records] == ["app_old", "app_new", "app_whole_seconds"]
    assert [r.record.data["modified_at"] for r in first.records] == [
        "2026-10-02T17:05:11.904417Z",
        "2026-10-14T09:41:55.568082Z",
        "2026-10-10T08:00:00Z",
    ]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state == {"modified_at": "2026-10-14T09:41:55.568082Z"}

    # A later sync that only sees older changes must keep the saved cursor instead of falling back to start_date.
    state = StateBuilder().with_stream_state("applications", first_state).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app_old", "modified_at": "2026-10-02T17:05:11.904417302Z"}]})
        second = _read("applications", state)

    assert [r.record.data["id"] for r in second.records] == ["app_old"]
    assert second.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_partition_state_advances_past_nanosecond_modified_at(stream_name):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"}]})
        mocker.get(
            re.compile(rf"^https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{stream_name}(\?.*)?$"),
            json={
                stream_name: [
                    {"id": f"{stream_name}_1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
                    {"id": f"{stream_name}_2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
                ]
            },
        )
        output = _read(stream_name)

    assert [r.record.data["id"] for r in output.records] == [f"{stream_name}_1", f"{stream_name}_2"]
    state = output.most_recent_state.stream_state.__dict__
    assert [(s["partition"]["app_id"], s["cursor"]) for s in state["states"]] == [
        ("app1", {"modified_at": "2026-10-14T09:41:55.568082Z"})
    ]
    assert state["state"] == {"modified_at": "2026-10-14T09:41:55.568082Z"}
