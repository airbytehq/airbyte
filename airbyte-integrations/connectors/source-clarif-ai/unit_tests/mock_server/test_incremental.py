# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models import AddFields
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test_key", "user_id": "test_user", "start_date": "2026-01-01T00:00:00Z"}
BASE_URL = "https://api.clarifai.com/v2/users/test_user/apps"
NEWEST = "2026-10-14T09:41:55.568082Z"


def read_records(stream_name, records, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with HttpMocker() as mocker:
        if stream_name != "applications":
            mocker.get(
                HttpRequest(BASE_URL, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(json.dumps({"apps": [{"id": "app1", "modified_at": "2026-01-01T00:00:00.000000Z"}]})),
            )
        request = HttpRequest(
            BASE_URL if stream_name == "applications" else f"{BASE_URL}/app1/{stream_name}",
            query_params={"page": "1", "per_page": "20" if stream_name == "applications" else "100"},
        )
        mocker.get(request, HttpResponse(json.dumps({"apps" if stream_name == "applications" else stream_name: records})))
        output = read(get_source(CONFIG, state), config=CONFIG, catalog=catalog, state=state)
        mocker.assert_number_of_calls(request, 1)
        assert not output.errors
    return output


def assert_cursor(output, stream_name, expected):
    state = output.state_messages[-1].state.stream.stream_state.__dict__
    if stream_name == "applications":
        assert state["modified_at"] == expected
    else:
        assert {entry["partition"]["app_id"]: entry["cursor"]["modified_at"] for entry in state["states"]} == {"app1": expected}


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_nanosecond_cursor_advances(stream_name):
    records = [
        {"id": "older", "modified_at": "2026-10-02T17:05:11.904417302Z"},
        {"id": "newest", "modified_at": "2026-10-14T09:41:55.568082659Z"},
    ]
    output = read_records(stream_name, records)
    assert [message.record.data["id"] for message in output.records] == ["older", "newest"]
    assert_cursor(output, stream_name, NEWEST)
    assert [message.record.data["modified_at"] for message in output.records] == ["2026-10-02T17:05:11.904417Z", NEWEST]


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_second_read_filters_client_side(stream_name):
    first = read_records(stream_name, [{"id": "first", "modified_at": "2026-10-14T09:41:55.568082659Z"}])
    state = [message.state for message in first.state_messages[-1:]]
    output = read_records(
        stream_name,
        [
            {"id": "older", "modified_at": "2026-10-02T17:05:11.904417302Z"},
            {"id": "boundary", "modified_at": "2026-10-14T09:41:55.568082999Z"},
            {"id": "next", "modified_at": "2026-10-14T09:41:55.568083001Z"},
        ],
        state,
    )
    assert [message.record.data["id"] for message in output.records] == ["boundary", "next"]
    assert [message.record.data["modified_at"] for message in output.records] == [NEWEST, "2026-10-14T09:41:55.568083Z"]
    assert_cursor(output, stream_name, "2026-10-14T09:41:55.568083Z")


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_timestamp_variants_and_missing_values(stream_name):
    records = [
        {"id": "nano", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        {"id": "micro", "modified_at": NEWEST},
        {"id": "short", "modified_at": "2026-10-14T09:41:55.1Z"},
        {"id": "whole", "modified_at": "2026-10-14T09:41:55Z"},
        {"id": "null", "modified_at": None},
        {"id": "missing"},
    ]
    output = read_records(stream_name, records)
    actual = {message.record.data["id"]: message.record.data for message in output.records}
    assert actual == {
        "nano": {"id": "nano", "modified_at": NEWEST},
        "micro": {"id": "micro", "modified_at": NEWEST},
        "short": {"id": "short", "modified_at": "2026-10-14T09:41:55.100000Z"},
        "whole": {"id": "whole", "modified_at": "2026-10-14T09:41:55.000000Z"},
        "null": {"id": "null"},
        "missing": {"id": "missing"},
    }
    assert_cursor(output, stream_name, NEWEST)


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_empty_read(stream_name):
    output = read_records(stream_name, [])
    assert not output.records


@pytest.mark.parametrize("record", [{}, {"modified_at": None}])
def test_normalization_leaves_absent_cursor_unchanged(record):
    definition = get_source(CONFIG).resolved_manifest["definitions"]["normalize_modified_at"]
    transformation = ModelToComponentFactory().create_component(AddFields, definition, CONFIG)
    original = record.copy()
    transformation.transform(record, config=CONFIG)
    assert record == original
