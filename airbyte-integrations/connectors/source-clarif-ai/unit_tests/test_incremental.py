# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2026-01-01T00:00:00Z",
}
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id"
_APPS_URL = re.compile(rf"{re.escape(_BASE_URL)}/apps(?:\?.*)?$")

# The Clarifai API returns modified_at with nanosecond (9-digit) fractional seconds.
_OLDER = "2026-10-02T17:05:11.904417302Z"
_NEWER = "2026-10-14T09:41:55.568082659Z"


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            json={"apps": [{"id": "app1", "modified_at": _OLDER}, {"id": "app2", "modified_at": _NEWER}]},
        )
        output = _read("applications")

    assert [(record.record.data["id"], record.record.data["modified_at"]) for record in output.records] == [
        ("app1", "2026-10-02T17:05:11.904417Z"),
        ("app2", "2026-10-14T09:41:55.568082Z"),
    ]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_app_substream_partition_state_advances_to_newest_nanosecond_modified_at(stream_name):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": _OLDER}]})
        mocker.get(
            re.compile(rf"{re.escape(_BASE_URL)}/apps/app1/{stream_name}(?:\?.*)?$"),
            json={stream_name: [{"id": "child1", "modified_at": _NEWER}, {"id": "child2", "modified_at": _OLDER}]},
        )
        output = _read(stream_name)

    assert [record.record.data["id"] for record in output.records] == ["child1", "child2"]
    partition_states = {
        state["partition"]["app_id"]: state["cursor"] for state in output.most_recent_state.stream_state.__dict__["states"]
    }
    assert partition_states == {"app1": {"modified_at": "2026-10-14T09:41:55.568082Z"}}
