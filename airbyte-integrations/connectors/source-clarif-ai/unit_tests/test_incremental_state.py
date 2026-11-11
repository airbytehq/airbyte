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
_START_DATE_AS_STATE = "2026-01-01T00:00:00.000000Z"
_APPS_URL = re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")
# Clarifai returns `modified_at` with nanosecond precision (nine fractional digits).
_APPS = [
    {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
]


def _child_url(app_id: str, resource: str) -> re.Pattern:
    return re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/{app_id}/{resource}(?:\?.*)?$")


def _read(stream_name: str, mocker: requests_mock.Mocker, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _stream_state(output) -> dict:
    return output.most_recent_state.stream_state.__dict__


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS})
        first_read = _read("applications", mocker)

        assert [record.record.data["id"] for record in first_read.records] == ["app1", "app2"]
        assert _stream_state(first_read) == {"modified_at": "2026-10-14T09:41:55.568082Z"}
        # The cursor value is emitted with the microsecond precision the cursor can parse.
        assert [record.record.data["modified_at"] for record in first_read.records] == [
            "2026-10-02T17:05:11.904417Z",
            "2026-10-14T09:41:55.568082Z",
        ]

        # The API has no `modified_at` filter and the connector does not filter client side, so the second
        # sync re-reads every app; the state it was given must be carried forward, not reset.
        state = StateBuilder().with_stream_state("applications", _stream_state(first_read)).build()
        second_read = _read("applications", mocker, state)

    assert [record.record.data["id"] for record in second_read.records] == ["app1", "app2"]
    assert _stream_state(second_read) == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize(
    "stream_name, resource",
    [
        pytest.param("datasets", "datasets", id="datasets"),
        pytest.param("models", "models", id="models"),
    ],
)
def test_substream_state_advances_per_app_to_newest_nanosecond_modified_at(stream_name, resource):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": _APPS})
        mocker.get(
            _child_url("app1", resource),
            json={
                resource: [
                    {"id": "app1_old", "modified_at": "2026-09-01T08:00:00.123456789Z"},
                    {"id": "app1_new", "modified_at": "2026-10-20T11:22:33.987654321Z"},
                ]
            },
        )
        mocker.get(_child_url("app2", resource), json={resource: [{"id": "app2_only", "modified_at": "2026-11-03T04:05:06.000000001Z"}]})
        first_read = _read(stream_name, mocker)

        assert sorted(record.record.data["id"] for record in first_read.records) == ["app1_new", "app1_old", "app2_only"]
        first_state = _stream_state(first_read)
        assert {partition["partition"]["app_id"]: partition["cursor"] for partition in first_state["states"]} == {
            "app1": {"modified_at": "2026-10-20T11:22:33.987654Z"},
            "app2": {"modified_at": "2026-11-03T04:05:06.000000Z"},
        }

        state = StateBuilder().with_stream_state(stream_name, first_state).build()
        second_read = _read(stream_name, mocker, state)

    # No server-side or client-side filtering: every record is re-read and each app keeps its cursor.
    assert sorted(record.record.data["id"] for record in second_read.records) == ["app1_new", "app1_old", "app2_only"]
    assert {partition["partition"]["app_id"]: partition["cursor"] for partition in _stream_state(second_read)["states"]} == {
        "app1": {"modified_at": "2026-10-20T11:22:33.987654Z"},
        "app2": {"modified_at": "2026-11-03T04:05:06.000000Z"},
    }
