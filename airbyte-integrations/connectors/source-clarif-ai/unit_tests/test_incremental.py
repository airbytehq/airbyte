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
_BASE = r"https://api\.clarifai\.com/v2/users/test_user_id/apps"
_QUERY = r"(?:\?.*)?$"
_START_STATE = "2026-01-01T00:00:00.000000Z"

# Clarifai returns protobuf timestamps with nanosecond precision (9 fractional digits).
_OLDER = "2026-10-02T17:05:11.904417302Z"
_NEWER = "2026-10-14T09:41:55.568082659Z"
_NEWER_TRUNCATED_TO_MICROSECONDS = "2026-10-14T09:41:55.568082Z"

_CHILD_STREAMS = {"datasets": "datasets", "models": "models"}


def _mock_api(mocker: requests_mock.Mocker, stream_name: str) -> None:
    records = [{"id": "rec_older", "modified_at": _OLDER}, {"id": "rec_newer", "modified_at": _NEWER}]
    if stream_name == "applications":
        mocker.get(re.compile(_BASE + _QUERY), [{"json": {"apps": records}}, {"json": {"apps": []}}])
        return
    mocker.get(re.compile(_BASE + _QUERY), [{"json": {"apps": [{"id": "app1", "modified_at": _OLDER}]}}, {"json": {"apps": []}}])
    path = _CHILD_STREAMS[stream_name]
    mocker.get(
        re.compile(_BASE + r"/app1/" + path + _QUERY),
        [{"json": {path: records}}, {"json": {path: []}}],
    )


def _cursor_value(stream_name: str, state_blob: dict) -> str:
    if stream_name == "applications":
        return state_blob["modified_at"]
    [partition_state] = [s for s in state_blob["states"] if s["partition"]["app_id"] == "app1"]
    return partition_state["cursor"]["modified_at"]


def _read(stream_name: str, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker, stream_name)
        return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_incremental_state_advances_to_newest_nanosecond_modified_at(stream_name):
    first = _read(stream_name)

    assert [r.record.data["id"] for r in first.records] == ["rec_older", "rec_newer"]
    assert first.records[1].record.data["modified_at"] == _NEWER_TRUNCATED_TO_MICROSECONDS
    first_state = first.most_recent_state.stream_state.__dict__
    assert _cursor_value(stream_name, first_state) == _NEWER_TRUNCATED_TO_MICROSECONDS

    # A later sync starting from the emitted state carries the cursor forward instead of resetting it to start_date.
    state = StateBuilder().with_stream_state(stream_name, first_state).build()
    second = _read(stream_name, state)

    assert [r.record.data["id"] for r in second.records] == ["rec_older", "rec_newer"]
    assert _cursor_value(stream_name, second.most_recent_state.stream_state.__dict__) == _NEWER_TRUNCATED_TO_MICROSECONDS
