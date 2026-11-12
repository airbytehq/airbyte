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

# Clarifai returns `modified_at` with nanosecond precision (9 fractional digits).
_APPS = [
    {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
]
_CHILDREN = {
    "app1": [{"id": "child-a", "modified_at": "2026-10-02T17:05:11.904417302Z"}],
    "app2": [
        {"id": "child-b", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        # Go-style RFC3339Nano drops the fractional part entirely when it is zero.
        {"id": "child-c", "modified_at": "2026-10-20T00:00:00Z"},
    ],
}


def _final_state(output, stream_name):
    states = [s.state.stream for s in output.state_messages if s.state.stream.stream_descriptor.name == stream_name]
    assert states, f"no state emitted for {stream_name}"
    return states[-1].stream_state.__dict__


def test_applications_state_advances_to_newest_nanosecond_modified_at_and_is_carried_forward():
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS})
        first = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert [r.record.data["id"] for r in first.records] == ["app1", "app2"]
    first_state = _final_state(first, "applications")
    assert first_state == {"modified_at": "2026-10-14T09:41:55.568082Z"}

    # The Clarifai list endpoints have no server-side modified_at filter and the connector does not
    # filter client-side, so every record is re-emitted; the state must carry forward and advance.
    state = StateBuilder().with_stream_state("applications", first_state).build()
    newer_app = {"id": "app3", "modified_at": "2026-11-01T08:00:00.123456789Z"}
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS + [newer_app]})
        second = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert [(r.record.data["id"], r.record.data["modified_at"]) for r in second.records] == [
        ("app1", "2026-10-02T17:05:11.904417Z"),
        ("app2", "2026-10-14T09:41:55.568082Z"),
        ("app3", "2026-11-01T08:00:00.123456Z"),
    ]
    assert _final_state(second, "applications") == {"modified_at": "2026-11-01T08:00:00.123456Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_app_substream_partition_cursors_advance_to_newest_nanosecond_modified_at(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS})
        for app_id, children in _CHILDREN.items():
            mocker.get(
                re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/{app_id}/{stream_name}(?:\?.*)?$"),
                json={stream_name: children},
            )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert sorted(r.record.data["id"] for r in output.records) == ["child-a", "child-b", "child-c"]
    state = _final_state(output, stream_name)
    partition_cursors = {s["partition"]["app_id"]: s["cursor"]["modified_at"] for s in state["states"]}
    assert partition_cursors == {
        "app1": "2026-10-02T17:05:11.904417Z",
        "app2": "2026-10-20T00:00:00.000000Z",
    }
