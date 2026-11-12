# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_INITIAL = "2026-01-01T00:00:00.000000Z"
_NEWEST = "2026-10-02T17:05:11.904417302Z"
_EXPECTED = "2026-10-02T17:05:11.904417Z"
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("nanoseconds", [True, False], ids=["nanoseconds", "microseconds"])
def test_nanosecond_cursor_advances_state(stream_name, nanoseconds):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    initial_state = {"modified_at": _INITIAL}
    if stream_name != "applications":
        initial_state = {"states": [{"partition": {"app_id": app_id}, "cursor": {"modified_at": _INITIAL}} for app_id in ["app1", "app2"]]}
    state = StateBuilder().with_stream_state(stream_name, initial_state).build()
    records = [
        {"id": "newest", "modified_at": _NEWEST if nanoseconds else _EXPECTED},
        {"id": "older", "modified_at": "2026-09-01T01:02:03.123456789Z" if nanoseconds else "2026-09-01T01:02:03.123456Z"},
    ]
    unchanged_records = [
        {"id": "missing"},
        {"id": "empty", "modified_at": ""},
        {"id": "seconds", "modified_at": "2026-09-01T01:02:03Z"},
        {"id": "milliseconds", "modified_at": "2026-09-01T01:02:03.123Z"},
    ]
    records += unchanged_records
    with HttpMocker() as mocker:
        mocker.get(
            HttpRequest(_BASE_URL, query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps({"apps": records if stream_name == "applications" else [{"id": "app1"}, {"id": "app2"}]})),
        )
        if stream_name != "applications":
            for app_id in ["app1", "app2"]:
                mocker.get(
                    HttpRequest(f"{_BASE_URL}/{app_id}/{stream_name}", query_params=ANY_QUERY_PARAMS),
                    HttpResponse(json.dumps({stream_name: records})),
                )
        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert not output.errors
    final_state = vars(output.most_recent_state.stream_state)
    if stream_name == "applications":
        assert final_state["modified_at"] == _EXPECTED
    else:
        assert {entry["partition"]["app_id"]: entry["cursor"]["modified_at"] for entry in final_state["states"]} == {
            "app1": _EXPECTED,
            "app2": _EXPECTED,
        }
    expected_records = [
        {"id": "newest", "modified_at": _EXPECTED},
        {"id": "older", "modified_at": "2026-09-01T01:02:03.123456Z"},
    ] + unchanged_records
    assert sorted((message.record.data for message in output.records), key=lambda record: record["id"]) == sorted(
        expected_records * (1 if stream_name == "applications" else 2), key=lambda record: record["id"]
    )
