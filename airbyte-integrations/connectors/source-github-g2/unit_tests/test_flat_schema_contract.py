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


def _assert_array_items_are_flat_objects(stream_name: str, field_name: str, item_schema: Mapping[str, Any]) -> None:
    assert item_schema.get("type") == "object", f"{stream_name}.{field_name}: object array items must be objects"
    assert item_schema.get("additionalProperties") is False, f"{stream_name}.{field_name}: item additionalProperties must be false"
    item_properties = item_schema.get("properties")
    assert isinstance(item_properties, dict), f"{stream_name}.{field_name}: item properties must be an object"
    for item_field_name, item_field_schema in item_properties.items():
        assert _is_scalar_type(
            item_field_schema.get("type")
        ), f"{stream_name}.{field_name}.{item_field_name}: item properties must have one scalar type"


def _assert_array_of_flat_objects(stream: Any, field_name: str, expected_fields: set[str]) -> None:
    schema = stream.get_json_schema()["properties"][field_name]
    assert schema.get("type") == ["null", "array"]
    item_schema = schema.get("items")
    assert isinstance(item_schema, dict)
    _assert_array_items_are_flat_objects(stream.name, field_name, item_schema)
    assert set(item_schema["properties"]) == expected_fields


def test_flatten_exemptions_are_exactly_the_approved_fields():
    assert {stream: set(fields) for stream, fields in FLATTEN_EXEMPTIONS.items()} == EXPECTED_EXEMPTION_KEYS


def test_manifest_declares_http_api_budget_with_policies():
    api_budget = make_source(config=CONFIG)._source_config["api_budget"]

    assert api_budget["type"] == "HTTPAPIBudget"
    assert api_budget["policies"]


def test_array_item_object_properties_must_be_scalar():
    with pytest.raises(AssertionError, match="item properties must have one scalar type"):
        _assert_array_items_are_flat_objects(
            "workflow_jobs",
            "steps",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {"nested": {"type": "object"}},
            },
        )


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
                item_schema_path = path.startswith("properties.") and path.endswith(".items") and path.count(".") == 2
                if key == "properties" and path and not item_schema_path:
                    raise AssertionError(f"{stream_name}.{path}: nested properties are forbidden")
                if key == "additionalProperties" and path and not item_schema_path:
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
            if item_schema.get("type") == "object":
                _assert_array_items_are_flat_objects(stream_name, field_name, item_schema)
            else:
                assert _is_scalar_type(item_schema.get("type")), f"{stream_name}.{field_name}: array items must have one scalar type"
        elif field_type == "array":
            item_schema = field_schema.get("items")
            assert isinstance(item_schema, dict), f"{stream_name}.{field_name}: array items schema is required"
            if item_schema.get("type") == "object":
                _assert_array_items_are_flat_objects(stream_name, field_name, item_schema)
            else:
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
    _assert_array_of_flat_objects(
        streams["workflow_jobs"],
        "steps",
        {"number", "name", "status", "conclusion", "started_at", "completed_at"},
    )
    _assert_array_of_flat_objects(streams["contributor_activity"], "weeks", {"w", "a", "d", "c"})
    _assert_array_of_flat_objects(
        streams["releases"],
        "assets",
        {
            "id",
            "node_id",
            "name",
            "digest",
            "content_type",
            "size",
            "download_count",
            "created_at",
            "updated_at",
            "browser_download_url",
            "url",
            "uploader_id",
            "uploader_login",
            "uploader_type",
        },
    )
