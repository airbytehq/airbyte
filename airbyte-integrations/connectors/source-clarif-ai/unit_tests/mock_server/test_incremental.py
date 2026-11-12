# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "newest,expected",
    [
        ("2026-10-14T09:41:55.568082659Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568Z"),
        ("2026-10-14T09:41:55Z", "2026-10-14T09:41:55Z"),
    ],
)
def test_nanosecond_cursor_advances(stream_name, newest, expected):
    records = [
        {"id": "newest", "modified_at": newest},
        {"id": "older", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "null", "modified_at": None},
        {"id": "missing"},
    ]
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    initial_cursor = {"modified_at": "2026-01-01T00:00:00.000000Z"}
    if stream_name == "applications":
        initial_state = initial_cursor
    else:
        initial_state = {"states": [{"partition": {"app_id": app_id}, "cursor": initial_cursor} for app_id in ["app1", "app2"]]}
    state = StateBuilder().with_stream_state(stream_name, initial_state).build()

    with HttpMocker() as mocker:
        if stream_name == "applications":
            mocker.get(
                HttpRequest(_BASE_URL, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(json.dumps({"apps": records})),
            )
        else:
            mocker.get(
                HttpRequest(_BASE_URL, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(json.dumps({"apps": [{"id": "app1"}, {"id": "app2"}]})),
            )
            for app_id in ["app1", "app2"]:
                mocker.get(
                    HttpRequest(f"{_BASE_URL}/{app_id}/{stream_name}", query_params={"page": "1", "per_page": "100"}),
                    HttpResponse(json.dumps({stream_name: records})),
                )
        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    expected_records = [
        {"id": "newest", "modified_at": expected},
        {"id": "older", "modified_at": "2026-10-02T17:05:11.904417Z"},
        {"id": "null"},
        {"id": "missing"},
    ]
    assert [message.record.data for message in output.records] == expected_records * (1 if stream_name == "applications" else 2)
    final_state = output.most_recent_state.stream_state.__dict__
    expected_state = datetime.fromisoformat(expected).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if stream_name == "applications":
        assert final_state["modified_at"] == expected_state
    else:
        assert {entry["partition"]["app_id"]: entry["cursor"] for entry in final_state["states"]} == {
            app_id: {"modified_at": expected_state} for app_id in ["app1", "app2"]
        }
