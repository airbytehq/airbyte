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
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "timestamp,expected",
    [
        ("2026-10-02T17:05:11.904417302Z", "2026-10-02T17:05:11.904417Z"),
        ("2026-10-02T17:05:11.904417Z", "2026-10-02T17:05:11.904417Z"),
        ("2026-10-02T17:05:11.904Z", "2026-10-02T17:05:11.904000Z"),
        ("2026-10-02T17:05:11Z", "2026-10-02T17:05:11.000000Z"),
    ],
)
def test_incremental_state(stream_name, timestamp, expected):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    apps = [
        {"id": "app1", "modified_at": timestamp},
        {"id": "app2", "modified_at": timestamp.replace("2026-10-02", "2026-10-03")},
    ]
    expected_records = apps if stream_name == "applications" else []
    with requests_mock.Mocker() as mocker:
        mocker.get(_BASE_URL, json={"apps": apps})
        if stream_name != "applications":
            for app in apps:
                records = [
                    {"id": app["id"] + "-newest", "modified_at": app["modified_at"]},
                    {"id": app["id"] + "-older", "modified_at": "2026-10-01T00:00:00.123456Z"},
                ]
                expected_records.extend(records)
                mocker.get(f"{_BASE_URL}/{app['id']}/{stream_name}", json={stream_name: records})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert not output.errors
    assert sorted(message.record.data["id"] for message in output.records) == sorted(record["id"] for record in expected_records)
    state = vars(output.most_recent_state.stream_state)
    if stream_name == "applications":
        assert state == {"modified_at": expected.replace("2026-10-02", "2026-10-03")}
    else:
        assert {
            item["partition"]["app_id"]: item["cursor"]["modified_at"] for item in state["states"]
        } == {"app1": expected, "app2": expected.replace("2026-10-02", "2026-10-03")}
    assert sorted(message.record.data["modified_at"] for message in output.records) == sorted(
        record["modified_at"][:26] + "Z" if len(record["modified_at"]) > 27 else record["modified_at"]
        for record in expected_records
    )


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_empty_incremental_read(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_BASE_URL, json={"apps": [] if stream_name == "applications" else [{"id": "app1"}]})
        if stream_name != "applications":
            mocker.get(f"{_BASE_URL}/app1/{stream_name}", json={stream_name: []})
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert not output.errors
    assert not output.records
