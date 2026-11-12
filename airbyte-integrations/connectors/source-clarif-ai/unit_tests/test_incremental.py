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
_APPS = [
    {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
]


def _mock_apps(mocker):
    mocker.get(_APPS_URL, json={"apps": _APPS})


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    with requests_mock.Mocker() as mocker:
        _mock_apps(mocker)
        output = _read("applications")

    assert [(record.record.data["id"], record.record.data["modified_at"]) for record in output.records] == [
        ("app1", "2026-10-02T17:05:11.904417Z"),
        ("app2", "2026-10-14T09:41:55.568082Z"),
    ]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}


def test_applications_second_read_carries_state_forward():
    state = StateBuilder().with_stream_state("applications", {"modified_at": "2026-10-14T09:41:55.568082Z"}).build()
    newer_app = {"id": "app3", "modified_at": "2026-11-01T08:00:00.123456789Z"}
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS + [newer_app]})
        output = _read("applications", state)

    # The connector has no server-side or client-side cursor filter, so every app is re-read on each sync.
    assert [record.record.data["id"] for record in output.records] == ["app1", "app2", "app3"]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-11-01T08:00:00.123456Z"}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_partition_state_advances_to_newest_nanosecond_modified_at(stream_name):
    with requests_mock.Mocker() as mocker:
        _mock_apps(mocker)
        for app_id, modified_at in (("app1", "2026-10-03T10:00:00.111111111Z"), ("app2", "2026-10-15T12:30:45.987654321Z")):
            mocker.get(
                re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/{app_id}/{stream_name}(?:\?.*)?$"),
                json={stream_name: [{"id": f"{app_id}-{stream_name}", "app_id": app_id, "modified_at": modified_at}]},
            )
        output = _read(stream_name)

    # Partitions are read concurrently, so record order across apps is not deterministic.
    assert sorted(record.record.data["id"] for record in output.records) == [f"app1-{stream_name}", f"app2-{stream_name}"]
    partition_state = {
        partition["partition"]["app_id"]: partition["cursor"] for partition in output.most_recent_state.stream_state.__dict__["states"]
    }
    assert partition_state == {
        "app1": {"modified_at": "2026-10-03T10:00:00.111111Z"},
        "app2": {"modified_at": "2026-10-15T12:30:45.987654Z"},
    }
