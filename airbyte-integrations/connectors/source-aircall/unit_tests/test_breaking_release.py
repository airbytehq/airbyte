# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.aircall.io/v1"
_CONFIG = {"api_id": "test-id", "api_token": "test-token"}


@pytest.fixture(scope="module")
def streams() -> dict:
    catalog = get_source(_CONFIG).discover(None, _CONFIG)
    return {stream.name: stream for stream in catalog.streams}


def _property(schema: dict, path: str) -> dict:
    node = schema
    for part in path.split("."):
        if part == "[]":
            node = node["items"]
        else:
            node = node["properties"][part]
    return node


@pytest.mark.parametrize(
    ("stream_name", "primary_key"),
    [
        pytest.param("calls", [["id"]], id="calls"),
        pytest.param("contacts", [["id"]], id="contacts"),
        pytest.param("webhooks", [["webhook_id"]], id="webhooks"),
    ],
)
def test_primary_keys(streams: dict, stream_name: str, primary_key: list) -> None:
    assert streams[stream_name].source_defined_primary_key == primary_key


def test_company_has_no_primary_key(streams: dict) -> None:
    assert not streams["company"].source_defined_primary_key


@pytest.mark.parametrize("stream_name", ["numbers", "teams"])
def test_numbers_and_teams_are_full_refresh_only(streams: dict, stream_name: str) -> None:
    stream = streams[stream_name]
    assert [mode.value for mode in stream.supported_sync_modes] == ["full_refresh"]
    assert not stream.default_cursor_field
    assert not stream.source_defined_cursor


@pytest.mark.parametrize(
    ("stream_name", "path"),
    [
        ("users", "created_at"),
        ("numbers", "created_at"),
        ("teams", "created_at"),
        ("teams", "users.[].created_at"),
        ("webhooks", "created_at"),
        ("calls", "user.created_at"),
        ("calls", "number.created_at"),
        ("calls", "teams.[].created_at"),
        ("calls", "comments.[].posted_by.created_at"),
        ("calls", "tags.[].tagged_by.created_at"),
    ],
)
def test_iso_datetime_strings_declare_date_time_format(streams: dict, stream_name: str, path: str) -> None:
    field = _property(streams[stream_name].json_schema, path)
    assert field["type"] == ["null", "string"]
    assert field.get("format") == "date-time"


@pytest.mark.parametrize(
    ("stream_name", "path", "expected_type"),
    [
        ("calls", "contact", ["null", "object"]),
        ("calls", "assigned_to", ["null", "object"]),
        ("calls", "transferred_by", ["null", "object"]),
        ("calls", "transferred_to", ["null", "object"]),
        ("calls", "number.priority", ["null", "integer"]),
        ("numbers", "priority", ["null", "integer"]),
        ("webhooks", "webhook_id", ["null", "string"]),
    ],
)
def test_declared_types_match_the_aircall_reference(streams: dict, stream_name: str, path: str, expected_type: list) -> None:
    assert _property(streams[stream_name].json_schema, path)["type"] == expected_type


def test_teams_schema_does_not_declare_webhook_id(streams: dict) -> None:
    assert "webhook_id" not in streams["teams"].json_schema["properties"]


@pytest.mark.parametrize("stream_name", ["numbers", "teams"])
def test_numbers_and_teams_full_refresh_emits_every_record_without_state(stream_name: str) -> None:
    request = HttpRequest(f"{_BASE_URL}/{stream_name}", query_params={"per_page": "50"})
    records = [
        {"id": 1, "created_at": "2023-10-03T18:35:43.000Z"},
        {"id": 2, "created_at": "2025-10-03T18:35:43Z"},
    ]
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({stream_name: records}), status_code=200))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert all("created_at" not in message.state.stream.stream_state.__dict__ for message in output.state_messages)
        http_mocker.assert_number_of_calls(request, 1)
