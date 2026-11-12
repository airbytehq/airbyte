# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2024-01-01T00:00:00Z"}
APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker


def mock_records(http_mocker, stream_name, records):
    if stream_name == "applications":
        url, key, page_size = APPS_URL, "apps", "20"
    else:
        http_mocker.get(
            HttpRequest(APPS_URL, query_params={"page": "1", "per_page": "20"}),
            HttpResponse(json.dumps({"apps": [{"id": "app1"}]})),
        )
        url, key, page_size = f"{APPS_URL}/app1/{stream_name}", stream_name, "100"
    http_mocker.get(
        HttpRequest(url, query_params={"page": "1", "per_page": page_size}),
        HttpResponse(json.dumps({key: records})),
    )


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "timestamps,expected_cursor",
    [
        (
            ["2026-10-02T17:05:11.904417302Z", "2026-10-14T09:41:55.568082937Z"],
            "2026-10-14T09:41:55.568082Z",
        ),
        (["2026-10-02T17:05:11Z", "2026-10-14T09:41:55Z"], "2026-10-14T09:41:55.000000Z"),
        (["2026-10-02T17:05:11.904417Z", "2026-10-14T09:41:55.568082Z"], "2026-10-14T09:41:55.568082Z"),
    ],
)
def test_incremental_state_advances(stream_name, timestamps, expected_cursor, http_mocker):
    records = [{"id": str(index), "modified_at": timestamp} for index, timestamp in enumerate(timestamps)]
    mock_records(http_mocker, stream_name, records)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    output = read(get_source(CONFIG), config=CONFIG, catalog=catalog)

    assert [message.record.data["id"] for message in output.records] == ["0", "1"]
    state = output.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        assert state["modified_at"] == expected_cursor
    else:
        assert state["state"]["modified_at"] == expected_cursor
        assert state["states"][0]["cursor"]["modified_at"] == expected_cursor
    assert [message.record.data["modified_at"] for message in output.records] == [
        timestamp[:26] + "Z" if len(timestamp) > 27 else timestamp for timestamp in timestamps
    ]
    assert not output.errors


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("records", [[], [{"id": "missing"}], [{"id": "null", "modified_at": None}]])
def test_empty_or_missing_cursor_is_not_added(stream_name, records, http_mocker):
    mock_records(http_mocker, stream_name, records)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(CONFIG), config=CONFIG, catalog=catalog)

    assert [message.record.data for message in output.records] == [{"id": record["id"]} for record in records]
    assert not output.errors
