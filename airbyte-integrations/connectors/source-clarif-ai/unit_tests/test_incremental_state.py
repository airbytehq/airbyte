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
_START_DATE_STATE = "2026-01-01T00:00:00.000000Z"
_OLDER = "2026-10-02T17:05:11.904417Z"
_STREAMS = [
    pytest.param("applications", "apps", id="applications"),
    pytest.param("datasets", "datasets", id="datasets"),
    pytest.param("models", "models", id="models"),
]
# Clarifai returns RFC 3339 timestamps whose fraction has 0, 3, 6 or 9 digits.
# Each case: the newest `modified_at` served by the API, the value emitted on the record, the cursor saved in the state.
_NEWEST_TIMESTAMPS = [
    pytest.param("2026-10-14T09:41:55.568082659Z", "2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z", id="nanoseconds"),
    pytest.param("2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z", id="microseconds"),
    pytest.param("2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568000Z", id="milliseconds"),
    pytest.param("2026-10-14T09:41:55Z", "2026-10-14T09:41:55Z", "2026-10-14T09:41:55.000000Z", id="whole_seconds"),
]


def _cursor_values(output, stream_name):
    """Return the cursor value(s) of the last state message emitted for the stream."""
    stream_state = output.most_recent_state.stream_state.__dict__
    assert output.most_recent_state.stream_descriptor.name == stream_name
    if stream_name == "applications":
        return [stream_state["modified_at"]]
    return [partition["cursor"]["modified_at"] for partition in stream_state["states"]]


@pytest.mark.parametrize("newest, emitted_newest, state_value", _NEWEST_TIMESTAMPS)
@pytest.mark.parametrize("stream_name, records_key", _STREAMS)
def test_incremental_state_advances_to_newest_modified_at(stream_name, records_key, newest, emitted_newest, state_value):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    child_url = f"{_APPS_URL}/app1/{stream_name}"

    with requests_mock.Mocker() as mocker:
        if stream_name == "applications":
            records = [{"id": "app1", "modified_at": _OLDER}, {"id": "app2", "modified_at": newest}]
            mocker.get(_APPS_URL, json={"apps": records})
        else:
            records = [{"id": "rec1", "modified_at": _OLDER}, {"id": "rec2", "modified_at": newest}]
            mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": newest}]})
            mocker.get(child_url, json={records_key: records})

        first_read = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert not first_read.errors
        assert [(record.record.data["id"], record.record.data["modified_at"]) for record in first_read.records] == [
            (records[0]["id"], _OLDER),
            (records[1]["id"], emitted_newest),
        ]
        assert _cursor_values(first_read, stream_name) == [state_value]

        # A later sync started from the emitted state must carry the cursor forward, not fall back to start_date.
        state = StateBuilder().with_stream_state(stream_name, first_read.most_recent_state.stream_state.__dict__).build()
        second_read = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

        assert not second_read.errors
        assert _cursor_values(second_read, stream_name) == [state_value]
        assert not [log for log in first_read.logs + second_read.logs if "cursor" in log.log.message.lower()]
