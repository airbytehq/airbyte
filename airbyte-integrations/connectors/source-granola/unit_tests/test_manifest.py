#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

CONNECTOR_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = CONNECTOR_DIR / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def notes_stream(manifest):
    return manifest["definitions"]["streams"]["notes"]


@pytest.fixture(scope="module")
def detailed_notes_stream(manifest):
    return manifest["definitions"]["streams"]["detailed_notes"]


@pytest.fixture(scope="module")
def notes_schema(manifest):
    return manifest["schemas"]["notes"]


def test_notes_cursor_field_is_updated_at(notes_stream):
    """The notes stream must use updated_at as cursor so edits are captured incrementally."""
    incremental_sync = notes_stream["incremental_sync"]
    assert incremental_sync["cursor_field"] == "updated_at"


def test_notes_start_time_option_uses_updated_after(notes_stream):
    """The API query parameter must be updated_after, not created_after."""
    start_time_option = notes_stream["incremental_sync"]["start_time_option"]
    assert start_time_option["field_name"] == "updated_after"


def test_notes_no_end_time_option(notes_stream):
    """The Granola API has no updated_before parameter, so end_time_option must not be set."""
    incremental_sync = notes_stream["incremental_sync"]
    assert "end_time_option" not in incremental_sync


def test_notes_no_step_or_cursor_granularity(notes_stream):
    """Without end_time_option, step and cursor_granularity should not be set."""
    incremental_sync = notes_stream["incremental_sync"]
    assert "step" not in incremental_sync
    assert "cursor_granularity" not in incremental_sync


def test_notes_datetime_format_is_iso8601(notes_stream):
    """The datetime_format should be full ISO 8601 to match the updated_after API parameter."""
    incremental_sync = notes_stream["incremental_sync"]
    assert incremental_sync["datetime_format"] == "%Y-%m-%dT%H:%M:%SZ"


def test_notes_schema_has_updated_at(notes_schema):
    """The notes schema must include the updated_at field."""
    assert "updated_at" in notes_schema["properties"]
    assert notes_schema["properties"]["updated_at"]["type"] == "string"
    assert notes_schema["properties"]["updated_at"]["format"] == "date-time"


def test_detailed_notes_incremental_dependency(detailed_notes_stream):
    """detailed_notes substream must have incremental_dependency: true to only fetch details for notes in the current incremental window."""
    parent_configs = detailed_notes_stream["retriever"]["partition_router"]["parent_stream_configs"]
    assert len(parent_configs) == 1
    assert parent_configs[0]["incremental_dependency"] is True


def test_concurrency_level_present(manifest):
    """concurrency_level must be set at the manifest root."""
    assert "concurrency_level" in manifest
    assert manifest["concurrency_level"]["type"] == "ConcurrencyLevel"
    assert manifest["concurrency_level"]["default_concurrency"] == 3


def test_api_budget_present(manifest):
    """api_budget must be set at the manifest root with a 5 req/s rate limit."""
    assert "api_budget" in manifest
    budget = manifest["api_budget"]
    assert budget["type"] == "HTTPAPIBudget"
    assert len(budget["policies"]) == 1
    policy = budget["policies"][0]
    assert policy["type"] == "FixedWindowCallRatePolicy"
    assert policy["call_limit"] == 5
    assert policy["period"] == "PT1S"


@pytest.mark.parametrize(
    "field_name,expected_type",
    [
        pytest.param("id", "string", id="id_field"),
        pytest.param("object", "string", id="object_field"),
        pytest.param("created_at", "string", id="created_at_field"),
        pytest.param("updated_at", "string", id="updated_at_field"),
    ],
)
def test_notes_schema_field_types(notes_schema, field_name, expected_type):
    """Verify notes schema field types are correct."""
    props = notes_schema["properties"]
    assert field_name in props
    field_type = props[field_name].get("type")
    if isinstance(field_type, list):
        assert expected_type in field_type
    else:
        assert field_type == expected_type


def test_notes_primary_key(notes_stream):
    """Verify the notes stream primary key is id."""
    assert notes_stream["primary_key"] == ["id"]


def test_detailed_notes_primary_key(detailed_notes_stream):
    """Verify the detailed_notes stream primary key is id."""
    assert detailed_notes_stream["primary_key"] == ["id"]


def test_notes_cursor_datetime_formats(notes_stream):
    """Verify the cursor_datetime_formats accept both with and without fractional seconds."""
    formats = notes_stream["incremental_sync"]["cursor_datetime_formats"]
    assert "%Y-%m-%dT%H:%M:%SZ" in formats
    assert "%Y-%m-%dT%H:%M:%S.%fZ" in formats


def test_base_requester_url(manifest):
    """Verify the base URL points to the Granola public API."""
    base_requester = manifest["definitions"]["base_requester"]
    assert base_requester["url_base"] == "https://public-api.granola.ai"


def test_base_requester_auth(manifest):
    """Verify Bearer token authentication is configured."""
    base_requester = manifest["definitions"]["base_requester"]
    auth = base_requester["authenticator"]
    assert auth["type"] == "BearerAuthenticator"
    assert auth["api_token"] == "{{ config['api_key'] }}"
