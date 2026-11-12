# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

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
_APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


def _catalog(stream_name):
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _state_of(output, stream_name):
    return [
        message.state.stream.stream_state.__dict__
        for message in output.state_messages
        if message.state.stream.stream_descriptor.name == stream_name
    ][-1]


def _app(app_id, modified_at):
    return {"id": app_id, "name": app_id, "modified_at": modified_at}


def test_applications_state_advances_to_nanosecond_cursor_across_reads():
    first_page = [
        _app("app-1", "2026-10-02T17:05:11.904417302Z"),
        _app("app-2", "2026-10-14T09:41:55.568082659Z"),
    ]
    with requests_mock.Mocker() as m:
        m.get(_APPS_URL, json={"apps": first_page})
        output = read(get_source(_CONFIG), _CONFIG, _catalog("applications"))

    state = _state_of(output, "applications")
    assert state == {"modified_at": "2026-10-14T09:41:55.568082Z"}
    assert [(r.record.data["id"], r.record.data["modified_at"]) for r in output.records] == [
        ("app-1", "2026-10-02T17:05:11.904417Z"),
        ("app-2", "2026-10-14T09:41:55.568082Z"),
    ]

    second_page = first_page + [_app("app-3", "2026-10-20T08:00:00.123456789Z")]
    state_input = StateBuilder().with_stream_state("applications", state).build()
    with requests_mock.Mocker() as m:
        m.get(_APPS_URL, json={"apps": second_page})
        output = read(get_source(_CONFIG, state_input), _CONFIG, _catalog("applications"), state_input)

    assert _state_of(output, "applications") == {"modified_at": "2026-10-20T08:00:00.123456Z"}
    # The apps endpoint has no modified_at filter and the cursor is not client-side, so every app is re-emitted.
    assert [r.record.data["id"] for r in output.records] == ["app-1", "app-2", "app-3"]


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_partition_state_advances_to_nanosecond_cursor(stream_name):
    with requests_mock.Mocker() as m:
        m.get(_APPS_URL, json={"apps": [_app("app-1", "2026-10-02T17:05:11.904417302Z")]})
        m.get(
            f"{_APPS_URL}/app-1/{stream_name}",
            json={
                stream_name: [
                    {"id": f"{stream_name}-1", "app_id": "app-1", "modified_at": "2026-10-03T10:00:00.000000001Z"},
                    {"id": f"{stream_name}-2", "app_id": "app-1", "modified_at": "2026-10-14T09:41:55.568082659Z"},
                ]
            },
        )
        output = read(get_source(_CONFIG), _CONFIG, _catalog(stream_name))

    state = _state_of(output, stream_name)
    partition_cursors = {s["partition"]["app_id"]: s["cursor"] for s in state["states"]}
    assert partition_cursors == {"app-1": {"modified_at": "2026-10-14T09:41:55.568082Z"}}
    assert [r.record.data["id"] for r in output.records] == [f"{stream_name}-1", f"{stream_name}-2"]
