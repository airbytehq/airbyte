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


def _final_state(output):
    return output.state_messages[-1].state.stream.stream_state.__dict__


def _ids(output):
    return [record.record.data["id"] for record in output.records]


def test_applications_state_advances_past_start_date_with_clarifai_timestamps():
    """Clarifai returns protobuf timestamps with 0, 3, 6 or 9 fractional digits; all of them must move the cursor."""
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    first_sync_apps = [
        {"id": "app_nanos", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "app_millis", "modified_at": "2026-10-05T08:00:00.123Z"},
        {"id": "app_seconds", "modified_at": "2026-10-10T12:30:45Z"},
        {"id": "app_newest", "modified_at": "2026-10-14T09:41:55.568082659Z"},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, [{"json": {"apps": first_sync_apps}}, {"json": {"apps": []}}])
        first = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert _ids(first) == ["app_nanos", "app_millis", "app_seconds", "app_newest"]
    assert [record.record.data["modified_at"] for record in first.records] == [
        "2026-10-02T17:05:11.904417Z",
        "2026-10-05T08:00:00.123Z",
        "2026-10-10T12:30:45Z",
        "2026-10-14T09:41:55.568082Z",
    ]
    first_state = _final_state(first)
    assert first_state == {"modified_at": "2026-10-14T09:41:55.568082Z"}

    # The apps endpoint has no modified_at filter and the stream does not filter client-side, so the next sync
    # re-emits every app; the cursor must start from the saved state and advance to the newly edited app.
    second_sync_apps = first_sync_apps + [{"id": "app_edited", "modified_at": "2026-11-01T10:00:00.000000001Z"}]
    state = StateBuilder().with_stream_state("applications", first_state).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, [{"json": {"apps": second_sync_apps}}, {"json": {"apps": []}}])
        second = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert _ids(second) == ["app_nanos", "app_millis", "app_seconds", "app_newest", "app_edited"]
    assert _final_state(second) == {"modified_at": "2026-11-01T10:00:00.000000Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_app_substream_partition_state_advances_with_nanosecond_modified_at(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    children_url = re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{stream_name}(?:\?.*)?$")
    children = [
        {"id": f"{stream_name}_1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": f"{stream_name}_2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            [{"json": {"apps": [{"id": "app1", "modified_at": "2026-10-01T00:00:00.000000001Z"}]}}, {"json": {"apps": []}}],
        )
        mocker.get(children_url, [{"json": {stream_name: children}}, {"json": {stream_name: []}}])
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert _ids(output) == [f"{stream_name}_1", f"{stream_name}_2"]
    partition_states = {
        state["partition"]["app_id"]: state["cursor"] for state in _final_state(output)["states"]
    }
    assert partition_states == {"app1": {"modified_at": "2026-10-14T09:41:55.568082Z"}}
