# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "timestamp,expected_cursor",
    [
        ("2026-10-14T09:41:55.568082659Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568000Z"),
        ("2026-10-14T09:41:55Z", "2026-10-14T09:41:55.000000Z"),
    ],
)
def test_incremental_state_advances_and_resumes(stream_name: str, timestamp: str, expected_cursor: str) -> None:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    old_timestamp = "2026-10-02T17:05:11.904417302Z"
    apps = [{"id": app_id, "modified_at": old_timestamp} for app_id in ("app1", "app2")]
    records = [
        {"id": "older", "modified_at": old_timestamp},
        {"id": "newest", "modified_at": timestamp},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{BASE_URL}?page=1&per_page=20", json={"apps": records if stream_name == "applications" else apps})
        if stream_name != "applications":
            for app_id in ("app1", "app2"):
                mocker.get(f"{BASE_URL}/{app_id}/{stream_name}?page=1&per_page=100", json={stream_name: records})
        first = read(get_source(CONFIG), config=CONFIG, catalog=catalog)

    assert not first.errors
    assert {message.record.data["id"] for message in first.records} == {"older", "newest"}
    state = first.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        assert state == {"modified_at": expected_cursor}
    else:
        assert {entry["partition"]["app_id"]: entry["cursor"] for entry in state["states"]} == {
            "app1": {"modified_at": expected_cursor},
            "app2": {"modified_at": expected_cursor},
        }

    saved_state = [message.state for message in first.state_messages]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{BASE_URL}?page=1&per_page=20", json={"apps": records if stream_name == "applications" else apps})
        if stream_name != "applications":
            for app_id in ("app1", "app2"):
                mocker.get(f"{BASE_URL}/{app_id}/{stream_name}?page=1&per_page=100", json={stream_name: records})
        second = read(get_source(CONFIG, state=saved_state), config=CONFIG, catalog=catalog, state=saved_state)

    assert not second.errors
    assert second.most_recent_state.stream_state.__dict__ == state
