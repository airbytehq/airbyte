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


def _catalog(stream_name):
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _stream_state(output, stream_name):
    states = [
        message.state.stream.stream_state for message in output.state_messages if message.state.stream.stream_descriptor.name == stream_name
    ]
    return states[-1].__dict__


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    apps = [
        {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        {"id": "app3", "modified_at": "2026-03-01T08:00:00.123456Z"},
        {"id": "app4", "modified_at": "2026-02-01T08:00:00Z"},
        {"id": "app5"},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": apps})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=_catalog("applications"))

    assert [record.record.data for record in output.records] == [
        {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417Z"},
        {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082Z"},
        {"id": "app3", "modified_at": "2026-03-01T08:00:00.123456Z"},
        {"id": "app4", "modified_at": "2026-02-01T08:00:00Z"},
        {"id": "app5"},
    ]
    assert _stream_state(output, "applications") == {"modified_at": "2026-10-14T09:41:55.568082Z"}


def test_applications_saved_cursor_carries_forward_across_syncs():
    state = StateBuilder().with_stream_state("applications", {"modified_at": "2026-10-02T17:05:11.904417Z"}).build()
    apps = [
        {"id": "app_old", "modified_at": "2026-09-30T00:00:00.000000001Z"},
        {"id": "app_same", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "app_new", "modified_at": "2026-10-14T09:41:55.568082659Z"},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": apps})
        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=_catalog("applications"), state=state)

    assert _stream_state(output, "applications") == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize(
    "stream_name,child_path,records_field",
    [("datasets", "datasets", "datasets"), ("models", "models", "models")],
)
def test_app_substream_state_advances_to_newest_nanosecond_modified_at(stream_name, child_path, records_field):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"}]})
        mocker.get(
            re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{child_path}(?:\?.*)?$"),
            json={
                records_field: [
                    {"id": f"{stream_name}1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
                    {"id": f"{stream_name}2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
                ]
            },
        )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=_catalog(stream_name))

    assert [record.record.data["id"] for record in output.records] == [f"{stream_name}1", f"{stream_name}2"]
    state = _stream_state(output, stream_name)
    assert [partition["cursor"] for partition in state["states"]] == [{"modified_at": "2026-10-14T09:41:55.568082Z"}]
