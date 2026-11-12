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

# Clarifai serializes timestamps with 0, 3, 6 or 9 fractional digits.
_NANOSECONDS = "2026-10-02T17:05:11.904417302Z"
_NANOSECONDS_TRUNCATED = "2026-10-02T17:05:11.904417Z"
_NEWEST_NANOSECONDS = "2026-10-14T09:41:55.568082659Z"
_NEWEST_NANOSECONDS_TRUNCATED = "2026-10-14T09:41:55.568082Z"
_WHOLE_SECOND = "2026-10-20T08:00:00Z"
_WHOLE_SECOND_AS_STATE = "2026-10-20T08:00:00.000000Z"


def _read(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)
    assert output.errors == []
    return output


def _emitted(output):
    return sorted((record.record.data["id"], record.record.data["modified_at"]) for record in output.records)


def _requested_urls(mocker):
    return sorted(request.url for request in mocker.request_history)


def test_applications_state_advances_to_newest_modified_at():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            json={
                "apps": [
                    {"id": "app1", "modified_at": _NANOSECONDS},
                    {"id": "app2", "modified_at": _NEWEST_NANOSECONDS},
                ]
            },
        )
        first_read = _read("applications")

    first_state = first_read.most_recent_state.stream_state.__dict__
    assert first_state == {"modified_at": _NEWEST_NANOSECONDS_TRUNCATED}
    assert _emitted(first_read) == [("app1", _NANOSECONDS_TRUNCATED), ("app2", _NEWEST_NANOSECONDS_TRUNCATED)]

    state = StateBuilder().with_stream_state("applications", first_state).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            json={
                "apps": [
                    {"id": "app1", "modified_at": _NANOSECONDS},
                    {"id": "app2", "modified_at": _WHOLE_SECOND},
                ]
            },
        )
        second_read = _read("applications", state)
        # The API has no modified_at filter, so the request is the same with or without state.
        assert _requested_urls(mocker) == [f"{_APPS_URL}?page=1&per_page=20"]

    # Every record is still emitted; only the saved state moves forward.
    assert _emitted(second_read) == [("app1", _NANOSECONDS_TRUNCATED), ("app2", _WHOLE_SECOND)]
    assert second_read.most_recent_state.stream_state.__dict__ == {"modified_at": _WHOLE_SECOND_AS_STATE}


@pytest.mark.parametrize(
    "stream_name, records_field",
    [
        pytest.param("datasets", "datasets", id="datasets"),
        pytest.param("models", "models", id="models"),
    ],
)
def test_substream_state_advances_per_app_partition(stream_name, records_field):
    def mock_api(mocker, app2_modified_at):
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": _NANOSECONDS}, {"id": "app2", "modified_at": _NANOSECONDS}]})
        mocker.get(f"{_APPS_URL}/app1/{stream_name}", json={records_field: [{"id": "a", "modified_at": _NANOSECONDS}]})
        mocker.get(f"{_APPS_URL}/app2/{stream_name}", json={records_field: [{"id": "b", "modified_at": app2_modified_at}]})

    def partition_cursors(output):
        return {
            partition_state["partition"]["app_id"]: partition_state["cursor"]
            for partition_state in output.most_recent_state.stream_state.__dict__["states"]
        }

    expected_urls = sorted(
        [
            f"{_APPS_URL}?page=1&per_page=20",
            f"{_APPS_URL}/app1/{stream_name}?page=1&per_page=100",
            f"{_APPS_URL}/app2/{stream_name}?page=1&per_page=100",
        ]
    )

    with requests_mock.Mocker() as mocker:
        mock_api(mocker, _NEWEST_NANOSECONDS)
        first_read = _read(stream_name)
        assert _requested_urls(mocker) == expected_urls

    assert partition_cursors(first_read) == {
        "app1": {"modified_at": _NANOSECONDS_TRUNCATED},
        "app2": {"modified_at": _NEWEST_NANOSECONDS_TRUNCATED},
    }
    assert _emitted(first_read) == [("a", _NANOSECONDS_TRUNCATED), ("b", _NEWEST_NANOSECONDS_TRUNCATED)]

    state = StateBuilder().with_stream_state(stream_name, first_read.most_recent_state.stream_state.__dict__).build()
    with requests_mock.Mocker() as mocker:
        mock_api(mocker, _WHOLE_SECOND)
        second_read = _read(stream_name, state)
        assert _requested_urls(mocker) == expected_urls

    # Every record is still emitted; only the saved state moves forward.
    assert _emitted(second_read) == [("a", _NANOSECONDS_TRUNCATED), ("b", _WHOLE_SECOND)]
    assert partition_cursors(second_read) == {
        "app1": {"modified_at": _NANOSECONDS_TRUNCATED},
        "app2": {"modified_at": _WHOLE_SECOND_AS_STATE},
    }
