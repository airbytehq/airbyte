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
_START_DATE_STATE = "2026-01-01T00:00:00.000000Z"
_APPS_URL = re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")

# Clarifai returns modified_at with nanosecond precision, e.g. 2026-10-14T09:41:55.568082659Z.
_APPS = [
    {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
]
_CHILD_RECORDS = {
    "app1": [
        {"id": "app1-old", "modified_at": "2026-03-01T08:00:00.123456789Z"},
        {"id": "app1-new", "modified_at": "2026-10-05T12:30:45.987654321Z"},
    ],
    "app2": [
        {"id": "app2-only", "modified_at": "2026-10-20T01:02:03.000000999Z"},
    ],
}


def _catalog(stream_name):
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _final_state(output):
    return output.state_messages[-1].state.stream.stream_state.__dict__


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    catalog = _catalog("applications")
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS})
        first = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert _final_state(first) == {"modified_at": "2026-10-14T09:41:55.568082Z"}
    assert [(record.record.data["id"], record.record.data["modified_at"]) for record in first.records] == [
        ("app1", "2026-10-02T17:05:11.904417Z"),
        ("app2", "2026-10-14T09:41:55.568082Z"),
    ]

    state = StateBuilder().with_stream_state("applications", _final_state(first)).build()
    newer_app = {"id": "app3", "modified_at": "2026-11-01T00:00:00.000000001Z"}
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS + [newer_app]})
        second = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    # The apps endpoint has no modified-since filter and the stream does not filter client-side, so every app is re-read;
    # the saved cursor is carried forward and advances to the newest app.
    assert [record.record.data["id"] for record in second.records] == ["app1", "app2", "app3"]
    assert _final_state(second) == {"modified_at": "2026-11-01T00:00:00.000000Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_partition_state_advances_to_newest_nanosecond_modified_at(stream_name):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS})
        for app_id, records in _CHILD_RECORDS.items():
            mocker.get(
                re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/{app_id}/{stream_name}(?:\?.*)?$"),
                json={stream_name: records},
            )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=_catalog(stream_name))

    assert sorted(record.record.data["id"] for record in output.records) == ["app1-new", "app1-old", "app2-only"]
    cursor_per_app = {
        partition_state["partition"]["app_id"]: partition_state["cursor"]["modified_at"]
        for partition_state in _final_state(output)["states"]
    }
    assert cursor_per_app == {
        "app1": "2026-10-05T12:30:45.987654Z",
        "app2": "2026-10-20T01:02:03.000000Z",
    }
    assert cursor_per_app["app1"] != _START_DATE_STATE
