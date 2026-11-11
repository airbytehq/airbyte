# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


def _read_stream(stream_name, records, sync_mode, state=None):
    apps = records if stream_name == "applications" else [{"id": "app1", "modified_at": "2026-10-01T00:00:00.000000Z"}]
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=_APPS_URL, query_params={"page": "1", "per_page": "20"}),
            HttpResponse(body=json.dumps({"apps": apps}), status_code=200),
        )
        if stream_name != "applications":
            http_mocker.get(
                HttpRequest(url=f"{_APPS_URL}/app1/{stream_name}", query_params={"page": "1", "per_page": "100"}),
                HttpResponse(body=json.dumps({stream_name: records}), status_code=200),
            )

        catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
        return read(get_source(_CONFIG, state=state), config=_CONFIG, catalog=catalog, state=state)


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_incremental_state_advances_for_nanosecond_cursors(stream_name):
    records = [
        {"id": "newest", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "older", "modified_at": "2026-10-01T17:05:11.123456Z"},
    ]
    output = _read_stream(stream_name, records, SyncMode.incremental)

    assert [message.record.data["id"] for message in output.records] == ["newest", "older"]
    state = output.most_recent_state.stream_state.__dict__
    if stream_name != "applications":
        assert len(state["states"]) == 1
        assert state["states"][0]["partition"] == {"app_id": "app1", "parent_slice": {}}
        state = state["states"][0]["cursor"]
    assert state == {"modified_at": "2026-10-02T17:05:11.904417Z"}
    assert [message.record.data["modified_at"] for message in output.records] == [
        "2026-10-02T17:05:11.904417Z",
        "2026-10-01T17:05:11.123456Z",
    ]
    resumed = _read_stream(
        stream_name,
        [{"id": "next", "modified_at": "2026-10-03T17:05:11.987654321Z"}, *records],
        SyncMode.incremental,
        state=[output.state_messages[-1].state],
    )
    # These list endpoints do not filter records by the saved cursor.
    assert [message.record.data["id"] for message in resumed.records] == ["next", "newest", "older"]
    resumed_state = resumed.most_recent_state.stream_state.__dict__
    if stream_name != "applications":
        resumed_state = resumed_state["states"][0]["cursor"]
    assert resumed_state == {"modified_at": "2026-10-03T17:05:11.987654Z"}


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "records",
    [
        [],
        [{"id": "missing"}, {"id": "null", "modified_at": None}],
        [{"id": "short", "modified_at": "2026-10-01T17:05:11.123Z"}],
    ],
)
def test_full_refresh_preserves_other_cursor_values(stream_name, records):
    output = _read_stream(stream_name, records, SyncMode.full_refresh)

    # Protocol serialization omits null object values, including on the unfixed source.
    assert [message.record.data for message in output.records] == [
        {key: value for key, value in record.items() if value is not None} for record in records
    ]
    assert not output.errors
