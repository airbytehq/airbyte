# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, Mapping

import pytest

from .utils import FLATTEN_EXEMPTIONS, make_source


SCALAR_TYPES = {"string", "integer", "number", "boolean"}
EXPECTED_EXEMPTION_KEYS = {"events": {"payload"}, "deployments": {"payload"}}
CONFIG = {"access_token": "test-token", "repository": "airbyte/test"}


def _discovered_streams():
    source = make_source(config=CONFIG)
    return {stream.name: stream for stream in source.streams(config=CONFIG)}


def _field_names(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        return []
    return [field for part in value for field in (part if isinstance(part, list) else [part]) if isinstance(field, str)]


def _primary_key_fields(stream: Any) -> list[str]:
    return _field_names(getattr(stream, "primary_key", None) or getattr(stream, "_primary_key", None))


def _is_scalar_type(value: Any) -> bool:
    if isinstance(value, str):
        return value in SCALAR_TYPES
    return (
        isinstance(value, list)
        and len(value) in (1, 2)
        and len(set(value)) == len(value)
        and set(value) <= SCALAR_TYPES | {"null"}
        and len(set(value) & SCALAR_TYPES) == 1
    )


def _assert_opaque_json(stream_name: str, field_name: str, schema: Mapping[str, Any]) -> None:
    assert set(schema) <= {"type"}, f"{stream_name}.{field_name}: opaque JSON must not be partially described"
    assert schema in (
        {},
        {"type": "object"},
        {"type": ["null", "object"]},
    ), f"{stream_name}.{field_name}: expected an opaque JSON declaration, got {schema!r}"


def test_flatten_exemptions_are_exactly_the_approved_fields():
    assert {stream: set(fields) for stream, fields in FLATTEN_EXEMPTIONS.items()} == EXPECTED_EXEMPTION_KEYS


def test_manifest_declares_http_api_budget_with_policies():
    api_budget = make_source(config=CONFIG)._source_config["api_budget"]

    assert api_budget["type"] == "HTTPAPIBudget"
    assert api_budget["policies"]


@pytest.mark.parametrize(
    "schema",
    [
        {"properties": {"nested": {"type": "object"}}},
        {"items": {"type": "string"}},
        {"oneOf": [{"type": "string"}]},
        {"additionalProperties": False},
        {"required": ["field"]},
    ],
)
def test_opaque_json_schema_rejects_partial_descriptions(schema):
    with pytest.raises(AssertionError, match="opaque JSON"):
        _assert_opaque_json("events", "payload", schema)


@pytest.mark.parametrize("stream_name,stream", list(_discovered_streams().items()))
def test_every_stream_has_a_flat_declared_schema(stream_name, stream):
    schema = stream.get_json_schema()
    assert schema.get("additionalProperties") is False, f"{stream_name}: root additionalProperties must be false"
    properties = schema.get("properties")
    assert isinstance(properties, dict), f"{stream_name}: root properties must be an object"

    def check_forbidden_keywords(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for keyword in ("oneOf", "anyOf", "allOf"):
                assert keyword not in value, f"{stream_name}.{path}: forbidden {keyword}"
            for key, nested in value.items():
                if key == "properties" and path:
                    raise AssertionError(f"{stream_name}.{path}: nested properties are forbidden")
                if key == "additionalProperties" and path:
                    raise AssertionError(f"{stream_name}.{path}: nested additionalProperties is forbidden")
                check_forbidden_keywords(nested, f"{path}.{key}" if path else key)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                check_forbidden_keywords(nested, f"{path}[{index}]")

    check_forbidden_keywords(schema, "")

    for field_name, field_schema in properties.items():
        if field_name in FLATTEN_EXEMPTIONS.get(stream_name, {}):
            _assert_opaque_json(stream_name, field_name, field_schema)
            continue
        field_type = field_schema.get("type")
        assert field_type is not None, f"{stream_name}.{field_name}: field type is required"
        if isinstance(field_type, list) and "array" in field_type:
            assert len(field_type) <= 2 and set(field_type) <= {
                "array",
                "null",
            }, f"{stream_name}.{field_name}: array type may only include null"
            item_schema = field_schema.get("items")
            assert isinstance(item_schema, dict), f"{stream_name}.{field_name}: array items schema is required"
            assert _is_scalar_type(item_schema.get("type")), f"{stream_name}.{field_name}: array items must have one scalar type"
        elif field_type == "array":
            item_schema = field_schema.get("items")
            assert isinstance(item_schema, dict), f"{stream_name}.{field_name}: array items schema is required"
            assert _is_scalar_type(item_schema.get("type")), f"{stream_name}.{field_name}: array items must have one scalar type"
        else:
            assert _is_scalar_type(field_type), f"{stream_name}.{field_name}: invalid flat field type {field_type!r}"

    for field_name in _primary_key_fields(stream):
        assert field_name in properties, f"{stream_name}: primary key field {field_name!r} is undeclared"
    for field_name in _field_names(stream.cursor_field):
        assert field_name in properties, f"{stream_name}: cursor field {field_name!r} is undeclared"


def test_flat_schema_contract_covers_all_39_streams():
    assert len(_discovered_streams()) == 39


def test_known_primary_keys_and_incremental_cursor_are_exposed():
    streams = _discovered_streams()
    assert _primary_key_fields(streams["issues"]) == ["id"]
    assert _primary_key_fields(streams["pull_requests"]) == ["id"]
    assert _field_names(streams["issues"].cursor_field) == ["updated_at"]
    asset_download_urls = streams["releases"].get_json_schema()["properties"]["asset_download_urls"]
    assert asset_download_urls.get("type") == ["null", "array"]
    assert asset_download_urls.get("items", {}).get("type") == ["null", "string"]
    assert "steps" not in streams["workflow_jobs"].get_json_schema()["properties"]
    assert "weeks" not in streams["contributor_activity"].get_json_schema()["properties"]
