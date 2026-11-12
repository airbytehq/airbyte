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

# `modified_at` is a protobuf timestamp: the API serializes it with 0, 3, 6 or 9 fractional digits.
_NANOSECONDS = ("2026-10-02T17:05:11.904417302Z", "2026-10-14T09:41:55.568082659Z")
_MICROSECONDS = ("2026-10-02T17:05:11.904417Z", "2026-10-14T09:41:55.568082Z")
_MILLISECONDS = ("2026-10-02T17:05:11.904Z", "2026-10-14T09:41:55.568Z")
_SECONDS = ("2026-10-02T17:05:11Z", "2026-10-14T09:41:55Z")

_PRECISIONS = [
    pytest.param(_NANOSECONDS, _MICROSECONDS, ["2026-10-02T17:05:11.904417Z", "2026-10-14T09:41:55.568082Z"], id="nanoseconds"),
    pytest.param(_MICROSECONDS, _MICROSECONDS, ["2026-10-02T17:05:11.904417Z", "2026-10-14T09:41:55.568082Z"], id="microseconds"),
    pytest.param(_MILLISECONDS, _MILLISECONDS, ["2026-10-02T17:05:11.904000Z", "2026-10-14T09:41:55.568000Z"], id="milliseconds"),
    pytest.param(_SECONDS, _SECONDS, ["2026-10-02T17:05:11.000000Z", "2026-10-14T09:41:55.000000Z"], id="seconds"),
]


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _final_state(output):
    return output.state_messages[-1].state.stream.stream_state.__dict__


@pytest.mark.parametrize("api_values, emitted_values, expected_cursors", _PRECISIONS)
def test_applications_state_advances_to_newest_modified_at(api_values, emitted_values, expected_cursors):
    older, newer = api_values
    # An app without `modified_at` is still emitted untouched and does not move the cursor.
    apps = [{"id": "app_old", "modified_at": older}, {"id": "app_new", "modified_at": newer}, {"id": "app_undated"}]

    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": apps})
        first_read = _read("applications")
        first_state = _final_state(first_read)
        second_read = _read("applications", StateBuilder().with_stream_state("applications", first_state).build())

    assert [record.record.data for record in first_read.records] == [
        {"id": "app_old", "modified_at": emitted_values[0]},
        {"id": "app_new", "modified_at": emitted_values[1]},
        {"id": "app_undated"},
    ]
    assert first_state == {"modified_at": expected_cursors[1]}
    # The API has no modified-since filter, so the second read re-reads both apps; the state is carried forward.
    assert [record.record.data["id"] for record in second_read.records] == ["app_old", "app_new", "app_undated"]
    assert _final_state(second_read) == first_state


@pytest.mark.parametrize("api_values, emitted_values, expected_cursors", _PRECISIONS)
@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_state_advances_per_app_partition(stream_name, api_values, emitted_values, expected_cursors):
    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": api_values[0]}, {"id": "app2", "modified_at": api_values[0]}]})
        mocker.get(f"{_APPS_URL}/app1/{stream_name}", json={stream_name: [{"id": "child1", "modified_at": api_values[0]}]})
        mocker.get(f"{_APPS_URL}/app2/{stream_name}", json={stream_name: [{"id": "child2", "modified_at": api_values[1]}]})
        output = _read(stream_name)

    assert sorted((record.record.data["id"], record.record.data["modified_at"]) for record in output.records) == [
        ("child1", emitted_values[0]),
        ("child2", emitted_values[1]),
    ]
    state = _final_state(output)
    assert sorted((partition["partition"]["app_id"], partition["cursor"]["modified_at"]) for partition in state["states"]) == [
        ("app1", expected_cursors[0]),
        ("app2", expected_cursors[1]),
    ]
    assert state["state"] == {"modified_at": expected_cursors[1]}
