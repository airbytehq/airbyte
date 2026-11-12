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
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"

# Clarifai returns `modified_at` with nanosecond precision (nine fractional digits).
_OLDER = "2026-10-02T17:05:11.904417302Z"
_NEWER = "2026-10-14T09:41:55.568082659Z"
# The cursor works at microsecond precision, so records and state keep the first six fractional digits.
_OLDER_MICROS = "2026-10-02T17:05:11.904417Z"
_NEWER_MICROS = "2026-10-14T09:41:55.568082Z"
# Clarifai omits the fraction when it is zero.
_WHOLE_SECOND = "2026-10-20T08:00:00Z"
_WHOLE_SECOND_STATE = "2026-10-20T08:00:00.000000Z"


def _mock_apps(mocker):
    return mocker.get(
        _BASE_URL,
        json={"apps": [{"id": "app1", "modified_at": _NEWER}, {"id": "app2", "modified_at": _OLDER}]},
    )


def _mock_child(mocker, stream_name, app_id, records):
    return mocker.get(f"{_BASE_URL}/{app_id}/{stream_name}", json={stream_name: records})


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _partition_cursors(stream_state):
    return {state["partition"]["app_id"]: state["cursor"]["modified_at"] for state in stream_state["states"]}


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    with requests_mock.Mocker() as mocker:
        _mock_apps(mocker)
        first_read = _read("applications")

        assert [record.record.data["id"] for record in first_read.records] == ["app1", "app2"]
        assert first_read.most_recent_state.stream_state.__dict__ == {"modified_at": _NEWER_MICROS}
        assert [record.record.data["modified_at"] for record in first_read.records] == [_NEWER_MICROS, _OLDER_MICROS]

        # A later sync that finds nothing newer carries the saved cursor forward instead of resetting it.
        state = StateBuilder().with_stream_state("applications", {"modified_at": _NEWER_MICROS}).build()
        second_read = _read("applications", state)

    # The API has no `modified_at` filter, so the stream re-reads every application (deduped downstream).
    assert [record.record.data["id"] for record in second_read.records] == ["app1", "app2"]
    assert second_read.most_recent_state.stream_state.__dict__ == {"modified_at": _NEWER_MICROS}
    assert second_read.errors == []


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_app_partitioned_stream_state_advances_per_app(stream_name):
    with requests_mock.Mocker() as mocker:
        _mock_apps(mocker)
        _mock_child(
            mocker,
            stream_name,
            "app1",
            [{"id": "a", "modified_at": _OLDER}, {"id": "b", "modified_at": _NEWER}],
        )
        _mock_child(mocker, stream_name, "app2", [{"id": "c", "modified_at": _WHOLE_SECOND}])
        first_read = _read(stream_name)

        assert sorted(record.record.data["id"] for record in first_read.records) == ["a", "b", "c"]
        first_state = first_read.most_recent_state.stream_state.__dict__
        assert _partition_cursors(first_state) == {"app1": _NEWER_MICROS, "app2": _WHOLE_SECOND_STATE}
        assert {record.record.data["id"]: record.record.data["modified_at"] for record in first_read.records} == {
            "a": _OLDER_MICROS,
            "b": _NEWER_MICROS,
            "c": _WHOLE_SECOND,
        }

        second_read = _read(stream_name, StateBuilder().with_stream_state(stream_name, first_state).build())

    assert sorted(record.record.data["id"] for record in second_read.records) == ["a", "b", "c"]
    assert _partition_cursors(second_read.most_recent_state.stream_state.__dict__) == {"app1": _NEWER_MICROS, "app2": _WHOLE_SECOND_STATE}
    assert second_read.errors == []
