# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def _read_records(stream_name, records):
    config = {
        "api_key": "test_api_key",
        "user_id": "test_user_id",
        "start_date": "2026-01-01T00:00:00Z",
    }
    apps_url = "https://api.clarifai.com/v2/users/test_user_id/apps"
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with HttpMocker() as mocker:
        if stream_name == "applications":
            url, key, page_size = apps_url, "apps", "20"
        else:
            mocker.get(
                HttpRequest(url=apps_url, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(body=json.dumps({"apps": [{"id": "app1"}]})),
            )
            url, key, page_size = f"{apps_url}/app1/{stream_name}", stream_name, "100"
        mocker.get(
            HttpRequest(url=url, query_params={"page": "1", "per_page": page_size}),
            HttpResponse(body=json.dumps({key: records})),
        )
        output = read(get_source(config), config=config, catalog=catalog)

    return output


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_nanosecond_cursor_advances_state(stream_name):
    output = _read_records(
        stream_name,
        [
            {"id": "older", "modified_at": "2026-10-13T09:41:55.123456789Z"},
            {"id": "newest", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        ],
    )
    state = output.most_recent_state.stream_state
    cursor = state.modified_at if stream_name == "applications" else state.states[0]["cursor"]["modified_at"]
    assert cursor == "2026-10-14T09:41:55.568082Z"
    if stream_name != "applications":
        assert state.state["modified_at"] == cursor
    assert len(output.records) == 2
    assert [message.record.data["modified_at"] for message in output.records] == [
        "2026-10-13T09:41:55.123456Z",
        "2026-10-14T09:41:55.568082Z",
    ]
    assert not output.errors


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "modified_at, expected",
    [
        ("2026-10-14T09:41:55.1234567Z", "2026-10-14T09:41:55.123456Z"),
        ("2026-10-14T09:41:55.12345678Z", "2026-10-14T09:41:55.123456Z"),
        ("2026-10-14T09:41:55.123456Z", "2026-10-14T09:41:55.123456Z"),
        ("2026-10-14T09:41:55.123Z", "2026-10-14T09:41:55.123Z"),
        ("2026-10-14T09:41:55.1Z", "2026-10-14T09:41:55.1Z"),
        ("2026-10-14T09:41:55Z", "2026-10-14T09:41:55Z"),
        ("invalid", "invalid"),
        ("", ""),
        (None, None),
    ],
)
def test_modified_at_normalization(stream_name, modified_at, expected):
    output = _read_records(stream_name, [{"id": "record1", "modified_at": modified_at}])
    assert output.records[0].record.data.get("modified_at") == expected
    assert not output.errors


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_empty_response_preserves_start_state(stream_name):
    output = _read_records(stream_name, [])
    assert not output.records
    state = output.most_recent_state.stream_state
    cursor = state.modified_at if stream_name == "applications" else state.states[0]["cursor"]["modified_at"]
    assert cursor == "2026-01-01T00:00:00.000000Z"
    assert not output.errors
