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
_APPS_URL = re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")


def _state_of(output):
    return output.most_recent_state.stream_state.__dict__


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = state or StateBuilder().build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def test_applications_state_advances_to_newest_nanosecond_modified_at_and_carries_forward():
    first_page = {
        "apps": [
            {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
            {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        ]
    }
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json=first_page)
        first = _read("applications")

    assert [record.record.data["id"] for record in first.records] == ["app1", "app2"]
    assert _state_of(first) == {"modified_at": "2026-10-14T09:41:55.568082Z"}

    # The next sync only sees an app older than the saved cursor: the saved cursor must be carried forward, not reset.
    state = StateBuilder().with_stream_state("applications", _state_of(first)).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"}]})
        second = _read("applications", state)

    assert _state_of(second) == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_app_substream_partition_state_advances_to_newest_nanosecond_modified_at(stream_name):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"}]})
        mocker.get(
            re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{stream_name}(?:\?.*)?$"),
            json={
                stream_name: [
                    {"id": "child1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
                    {"id": "child2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
                ]
            },
        )
        output = _read(stream_name)

    assert [record.record.data["id"] for record in output.records] == ["child1", "child2"]
    partition_states = {state["partition"]["app_id"]: state["cursor"] for state in _state_of(output)["states"]}
    assert partition_states == {"app1": {"modified_at": "2026-10-14T09:41:55.568082Z"}}
