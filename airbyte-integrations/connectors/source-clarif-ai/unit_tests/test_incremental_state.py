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
_BASE = "https://api.clarifai.com/v2/users/test_user_id/apps"

# Clarifai returns modified_at with nanosecond precision (9 fractional digits).
_OCT_02 = "2026-10-02T17:05:11.904417302Z"
_OCT_14 = "2026-10-14T09:41:55.568082659Z"
_NOV_03 = "2026-11-03T08:00:01.000000123Z"


def _mock_list(mocker, path, key, records):
    mocker.get(
        re.compile(rf"{re.escape(_BASE + path)}(?:\?.*)?$"),
        [{"json": {key: records}}, {"json": {key: []}}],
    )


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    source = get_source(_CONFIG, state=state)
    return read(source, config=_CONFIG, catalog=catalog, state=state)


def _state(output):
    return output.most_recent_state.stream_state.__dict__


def test_applications_state_advances_to_newest_modified_at_and_is_carried_forward():
    with requests_mock.Mocker() as mocker:
        _mock_list(mocker, "", "apps", [{"id": "app1", "modified_at": _OCT_02}, {"id": "app2", "modified_at": _OCT_14}])
        first = _read("applications")

    assert [(r.record.data["id"], r.record.data["modified_at"]) for r in first.records] == [
        ("app1", "2026-10-02T17:05:11.904417Z"),
        ("app2", "2026-10-14T09:41:55.568082Z"),
    ]
    assert _state(first) == {"modified_at": "2026-10-14T09:41:55.568082Z"}

    state = StateBuilder().with_stream_state("applications", _state(first)).build()
    with requests_mock.Mocker() as mocker:
        _mock_list(mocker, "", "apps", [{"id": "app2", "modified_at": _OCT_14}, {"id": "app3", "modified_at": _NOV_03}])
        second = _read("applications", state=state)

    assert [r.record.data["id"] for r in second.records] == ["app2", "app3"]
    assert _state(second) == {"modified_at": "2026-11-03T08:00:01.000000Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_partition_state_advances_to_newest_modified_at(stream_name):
    with requests_mock.Mocker() as mocker:
        _mock_list(mocker, "", "apps", [{"id": "app1", "modified_at": _OCT_02}, {"id": "app2", "modified_at": _OCT_14}])
        _mock_list(mocker, f"/app1/{stream_name}", stream_name, [{"id": "a1", "modified_at": _OCT_14}])
        _mock_list(mocker, f"/app2/{stream_name}", stream_name, [{"id": "a2", "modified_at": _OCT_02}])
        output = _read(stream_name)

    assert sorted(r.record.data["id"] for r in output.records) == ["a1", "a2"]
    state = _state(output)
    assert {s["partition"]["app_id"]: s["cursor"]["modified_at"] for s in state["states"]} == {
        "app1": "2026-10-14T09:41:55.568082Z",
        "app2": "2026-10-02T17:05:11.904417Z",
    }
