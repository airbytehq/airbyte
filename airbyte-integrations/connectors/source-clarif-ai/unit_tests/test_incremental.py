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
_APPS_URL = re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")
_NEWER_NANOS = "2026-10-14T09:41:55.568082659Z"
_OLDER_NANOS = "2026-10-02T17:05:11.904417302Z"


def _read_incremental(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            json={"apps": [{"id": "app1", "modified_at": _OLDER_NANOS}, {"id": "app2", "modified_at": _NEWER_NANOS}]},
        )
        output = _read_incremental("applications")

    assert [record.record.data["id"] for record in output.records] == ["app1", "app2"]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize(("stream_name", "path"), [("datasets", "datasets"), ("models", "models")])
def test_app_substream_state_advances_per_partition_with_nanosecond_modified_at(stream_name, path):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": _OLDER_NANOS}]})
        mocker.get(
            re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{path}(?:\?.*)?$"),
            json={path: [{"id": "child1", "modified_at": _OLDER_NANOS}, {"id": "child2", "modified_at": _NEWER_NANOS}]},
        )
        output = _read_incremental(stream_name)

    assert [record.record.data["id"] for record in output.records] == ["child1", "child2"]
    state = output.most_recent_state.stream_state.__dict__
    assert [(s["partition"], s["cursor"]) for s in state["states"]] == [
        ({"app_id": "app1", "parent_slice": {}}, {"modified_at": "2026-10-14T09:41:55.568082Z"})
    ]
