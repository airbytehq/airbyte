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
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
_APPS_URL = re.compile(r"^https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")
_START_DATE_STATE = "2026-01-01T00:00:00.000000Z"

# Clarifai returns `modified_at` with nanosecond precision; some values have fewer fractional digits.
_OLDER = "2026-10-02T17:05:11.904417302Z"
_NEWEST = "2026-10-14T09:41:55.568082659Z"
_OLDER_STATE = "2026-10-02T17:05:11.904417Z"
_NEWEST_STATE = "2026-10-14T09:41:55.568082Z"
_SECOND_PRECISION = "2026-10-20T08:00:00Z"
_SECOND_PRECISION_STATE = "2026-10-20T08:00:00.000000Z"


def _app(app_id, modified_at):
    return {"id": app_id, "modified_at": modified_at}


def _mock_children(mocker, stream_name, app_id, records):
    return mocker.get(
        re.compile(rf"^{re.escape(_BASE_URL)}/{app_id}/{stream_name}(?:\?.*)?$"),
        json={stream_name: records},
    )


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _partition_cursors(stream_state):
    return {entry["partition"]["app_id"]: entry["cursor"]["modified_at"] for entry in stream_state["states"]}


@pytest.mark.parametrize(
    "newest_modified_at, expected_state",
    [
        pytest.param(_NEWEST, _NEWEST_STATE, id="nanosecond_precision"),
        pytest.param(_SECOND_PRECISION, _SECOND_PRECISION_STATE, id="second_precision"),
    ],
)
def test_applications_state_advances_to_newest_modified_at(newest_modified_at, expected_state):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [_app("app1", _OLDER), _app("app2", newest_modified_at)]})
        output = _read("applications")

    assert [record.record.data["id"] for record in output.records] == ["app1", "app2"]
    assert output.most_recent_state.stream_state.__dict__ == {"modified_at": expected_state}
    assert not [log for log in output.logs if "cursor" in log.log.message.lower()]


def test_applications_emits_modified_at_trimmed_to_microseconds():
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [_app("app1", _OLDER), _app("app2", _SECOND_PRECISION), {"id": "app3"}]})
        output = _read("applications")

    # Only fractional digits beyond microseconds are dropped; other values and records without the field are untouched.
    assert [record.record.data for record in output.records] == [
        {"id": "app1", "modified_at": _OLDER_STATE},
        {"id": "app2", "modified_at": _SECOND_PRECISION},
        {"id": "app3"},
    ]


@pytest.mark.parametrize(
    "previous_state",
    [
        pytest.param(None, id="state_from_first_read"),
        pytest.param({"modified_at": _START_DATE_STATE}, id="state_stuck_at_start_date"),
    ],
)
def test_applications_second_read_carries_state_forward(previous_state):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [_app("app1", _OLDER), _app("app2", _NEWEST)]})
        if previous_state is None:
            previous_state = _read("applications").most_recent_state.stream_state.__dict__
            assert previous_state == {"modified_at": _NEWEST_STATE}
        state = StateBuilder().with_stream_state("applications", previous_state).build()
        second_output = _read("applications", state)

    # The endpoint has no date filter, so the second read re-emits every record; the state must not regress.
    assert [record.record.data["id"] for record in second_output.records] == ["app1", "app2"]
    assert second_output.most_recent_state.stream_state.__dict__ == {"modified_at": _NEWEST_STATE}


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_state_advances_per_app_partition(stream_name):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [_app("app1", _OLDER), _app("app2", _OLDER)]})
        _mock_children(mocker, stream_name, "app1", [{"id": "a", "modified_at": _OLDER}, {"id": "b", "modified_at": _NEWEST}])
        _mock_children(mocker, stream_name, "app2", [{"id": "c", "modified_at": _OLDER}])
        output = _read(stream_name)

    assert sorted(record.record.data["id"] for record in output.records) == ["a", "b", "c"]
    assert _partition_cursors(output.most_recent_state.stream_state.__dict__) == {
        "app1": _NEWEST_STATE,
        "app2": _OLDER_STATE,
    }
