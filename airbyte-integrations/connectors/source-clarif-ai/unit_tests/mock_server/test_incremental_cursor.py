# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AddFields
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "cursor_fields,expected_fields,expected_cursor",
    [
        ({"modified_at": "2024-10-02T17:05:11.904417302Z"}, {"modified_at": "2024-10-02T17:05:11.904417Z"}, "2024-10-02T17:05:11.904417Z"),
        ({"modified_at": "2024-10-02T17:05:11.904417Z"}, {"modified_at": "2024-10-02T17:05:11.904417Z"}, "2024-10-02T17:05:11.904417Z"),
        ({"modified_at": "2024-10-02T17:05:11.904Z"}, {"modified_at": "2024-10-02T17:05:11.904Z"}, "2024-10-02T17:05:11.904000Z"),
        ({"modified_at": "2024-10-02T17:05:11Z"}, {"modified_at": "2024-10-02T17:05:11Z"}, "2024-10-02T17:05:11.000000Z"),
        ({"modified_at": None}, {}, "2024-01-01T00:00:00.000000Z"),
        ({}, {}, "2024-01-01T00:00:00.000000Z"),
    ],
    ids=["nanoseconds", "microseconds", "milliseconds", "seconds", "null", "missing"],
)
@pytest.mark.parametrize("existing_state", [False, True], ids=["fresh", "resume"])
def test_incremental_cursor(stream_name, cursor_fields, expected_fields, expected_cursor, existing_state):
    config = {
        "api_key": "test_api_key",
        "user_id": "test_user_id",
        "start_date": "2024-01-01T00:00:00Z",
    }
    records = [
        {"id": "newest", **cursor_fields},
        {
            "id": "older",
            **{key: value.replace("10-02", "10-01") if isinstance(value, str) else value for key, value in cursor_fields.items()},
        },
    ]
    apps_url = "https://api.clarifai.com/v2/users/test_user_id/apps"
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    initial_state = StateBuilder()
    if existing_state:
        initial_state.with_stream_state(stream_name, {"modified_at": "2024-01-01T00:00:00.000000Z"})
    initial_state = initial_state.build()

    with requests_mock.Mocker() as mocker:
        if stream_name == "applications":
            mocker.get(apps_url, json={"apps": records})
        else:
            mocker.get(apps_url, json={"apps": [{"id": "parent_app"}]})
            mocker.get(f"{apps_url}/parent_app/{stream_name}", json={stream_name: records})
        output = read(get_source(config, state=initial_state), config=config, catalog=catalog, state=initial_state)

    output.raise_if_errors()
    assert [message.record.data["id"] for message in output.records] == ["newest", "older"]
    assert output.records[0].record.data == {"id": "newest", **expected_fields}
    assert output.records[1].record.data == {
        "id": "older",
        **{key: value.replace("10-02", "10-01") if isinstance(value, str) else value for key, value in expected_fields.items()},
    }
    state = vars(output.most_recent_state.stream_state)
    if "states" in state:
        assert len(state["states"]) == 1
        assert state["states"][0]["partition"]["app_id"] == "parent_app"
        state = state["states"][0]["cursor"]
    assert state == {"modified_at": expected_cursor}


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("cursor_fields", [{"modified_at": None}, {}], ids=["null", "missing"])
def test_transformation_preserves_absent_cursor(stream_name, cursor_fields):
    config = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2024-01-01T00:00:00Z"}
    stream = get_source(config).resolved_manifest["definitions"]["streams"][stream_name]
    record = {"id": "record", **cursor_fields}
    for definition in stream.get("transformations", []):
        transformation = ModelToComponentFactory().create_component(AddFields, definition, config)
        transformation.transform(record, config=config)
    assert record == {"id": "record", **cursor_fields}
