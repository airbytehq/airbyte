# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2024-01-01T00:00:00Z",
}
_APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "modified_at, expected_cursor",
    [
        ("2026-10-02T17:05:11.904417302Z", "2026-10-02T17:05:11.904417Z"),
        ("2026-10-14T09:41:55.568082659Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-02T17:05:11.904417Z", "2026-10-02T17:05:11.904417Z"),
    ],
)
def test_incremental_state_advances(stream_name, modified_at, expected_cursor):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    record = {"id": "record1", "modified_at": modified_at}

    with requests_mock.Mocker() as mocker:
        mocker.get(
            _APPS_URL,
            json={"apps": [record] if stream_name == "applications" else [{"id": "app1"}]},
        )
        if stream_name != "applications":
            mocker.get(f"{_APPS_URL}/app1/{stream_name}", json={stream_name: [record]})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert not output.errors
    assert len(output.records) == 1
    state = output.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        assert state["modified_at"] == expected_cursor
    else:
        assert state["states"] == [
            {"partition": {"app_id": "app1", "parent_slice": {}}, "cursor": {"modified_at": expected_cursor}}
        ]
    assert output.records[0].record.data["modified_at"] == expected_cursor


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "records",
    [[], [{"id": "record1"}], [{"id": "record1", "modified_at": None}], [{"id": "record1", "modified_at": "invalid"}]],
)
def test_empty_or_unparseable_cursor_does_not_advance_state(stream_name, records):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": records if stream_name == "applications" else [{"id": "app1"}]})
        if stream_name != "applications":
            mocker.get(f"{_APPS_URL}/app1/{stream_name}", json={stream_name: records})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert not output.errors
    assert len(output.records) == len(records)
    state = output.most_recent_state.stream_state.__dict__
    expected_cursor = {"modified_at": "2024-01-01T00:00:00.000000Z"}
    if stream_name == "applications":
        assert state == expected_cursor
    else:
        assert state["states"] == [{"partition": {"app_id": "app1", "parent_slice": {}}, "cursor": expected_cursor}]
