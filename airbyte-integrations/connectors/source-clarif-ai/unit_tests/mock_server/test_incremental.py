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
_BASE = "https://api.clarifai.com/v2/users/test_user_id/apps"
# Clarifai returns RFC 3339 timestamps with nanosecond (9-digit) fractional seconds.
_APP_MODIFIED_AT = "2026-10-14T09:41:55.568082659Z"
_CHILD_MODIFIED_AT = "2026-10-02T17:05:11.904417302Z"
_APP_STATE_AFTER_FIRST_READ = "2026-10-14T09:41:55.568082Z"
_CHILD_STATE_AFTER_FIRST_READ = "2026-10-02T17:05:11.904417Z"


def _mock_api(mocker: requests_mock.Mocker) -> None:
    mocker.get(
        re.compile(rf"{re.escape(_BASE)}\?.*"),
        json={"apps": [{"id": "app1", "modified_at": _APP_MODIFIED_AT}]},
    )
    for child in ("datasets", "models"):
        mocker.get(
            re.compile(rf"{re.escape(_BASE)}/app1/{child}\?.*"),
            json={child: [{"id": f"{child}1", "modified_at": _CHILD_MODIFIED_AT}]},
        )


def _cursor_values(output, stream_name):
    """Return every cursor value written to state for stream_name (per partition for substreams)."""
    values = []
    for message in output.state_messages:
        stream_state = message.state.stream
        if stream_state.stream_descriptor.name != stream_name:
            continue
        state = stream_state.stream_state.__dict__
        if "states" in state:
            values.extend(partition["cursor"]["modified_at"] for partition in state["states"])
        else:
            values.append(state["modified_at"])
    return values


@pytest.mark.parametrize(
    "stream_name, expected_state",
    [
        ("applications", _APP_STATE_AFTER_FIRST_READ),
        ("datasets", _CHILD_STATE_AFTER_FIRST_READ),
        ("models", _CHILD_STATE_AFTER_FIRST_READ),
    ],
)
def test_incremental_state_advances_to_newest_nanosecond_modified_at(stream_name, expected_state):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        first = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in first.records] == ["app1" if stream_name == "applications" else f"{stream_name}1"]
    # The emitted value is trimmed to microseconds so it matches the cursor that is written to state.
    assert [record.record.data["modified_at"] for record in first.records] == [expected_state]
    assert _cursor_values(first, stream_name)[-1] == expected_state

    # A second read resumes from the emitted state and does not fall back to start_date.
    state = StateBuilder().with_stream_state(stream_name, first.most_recent_state.stream_state.__dict__).build()
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        second = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert [record.record.data["id"] for record in second.records] == ["app1" if stream_name == "applications" else f"{stream_name}1"]
    assert _cursor_values(second, stream_name)[-1] == expected_state
    assert "2026-01-01T00:00:00.000000Z" not in _cursor_values(second, stream_name)
