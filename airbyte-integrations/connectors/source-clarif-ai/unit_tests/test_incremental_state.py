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


def _app(app_id, modified_at):
    return {"id": app_id, "user_id": "test_user_id", "modified_at": modified_at}


@pytest.mark.parametrize(
    "newest_modified_at, expected_cursor",
    [
        pytest.param("2026-10-14T09:41:55.568082659Z", "2026-10-14T09:41:55.568082Z", id="nanoseconds"),
        pytest.param("2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z", id="microseconds"),
        pytest.param("2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568000Z", id="milliseconds"),
        pytest.param("2026-10-14T09:41:55Z", "2026-10-14T09:41:55.000000Z", id="whole_seconds"),
    ],
)
def test_applications_state_advances_to_newest_modified_at(newest_modified_at, expected_cursor):
    with requests_mock.Mocker() as m:
        m.get(
            _APPS_URL,
            [
                {"json": {"apps": [_app("app-1", "2026-10-02T17:05:11.904417302Z"), _app("app-2", newest_modified_at)]}},
                {"json": {"apps": []}},
            ],
        )
        output = read(get_source(_CONFIG), _CONFIG, _catalog("applications"))

    assert [r.record.data["id"] for r in output.records] == ["app-1", "app-2"]
    assert output.records[1].record.data["modified_at"] == (newest_modified_at if len(newest_modified_at) <= 27 else expected_cursor)
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": expected_cursor}


def test_applications_second_sync_carries_state_forward():
    state = StateBuilder().with_stream_state("applications", {"modified_at": "2026-10-02T17:05:11.904417Z"}).build()
    with requests_mock.Mocker() as m:
        m.get(
            _APPS_URL,
            [
                {
                    "json": {
                        "apps": [
                            _app("app-old", "2026-09-30T08:00:00.000000001Z"),
                            _app("app-1", "2026-10-02T17:05:11.904417302Z"),
                            _app("app-2", "2026-10-14T09:41:55.568082659Z"),
                        ]
                    }
                },
                {"json": {"apps": []}},
            ],
        )
        output = read(get_source(_CONFIG, state), _CONFIG, _catalog("applications"), state)

    assert [r.record.data["id"] for r in output.records] == ["app-old", "app-1", "app-2"]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": "2026-10-14T09:41:55.568082Z"}


def test_datasets_partition_state_advances_to_newest_modified_at():
    with requests_mock.Mocker() as m:
        m.get(_APPS_URL, [{"json": {"apps": [_app("app-1", "2026-10-02T17:05:11.904417302Z")]}}, {"json": {"apps": []}}])
        m.get(
            "https://api.clarifai.com/v2/users/test_user_id/apps/app-1/datasets",
            [
                {"json": {"datasets": [{"id": "ds-1", "app_id": "app-1", "modified_at": "2026-10-14T09:41:55.568082659Z"}]}},
                {"json": {"datasets": []}},
            ],
        )
        output = read(get_source(_CONFIG), _CONFIG, _catalog("datasets"))

    assert [r.record.data["id"] for r in output.records] == ["ds-1"]
    states = output.most_recent_state.stream_state.__dict__["states"]
    assert [s["cursor"] for s in states] == [{"modified_at": "2026-10-14T09:41:55.568082Z"}]
