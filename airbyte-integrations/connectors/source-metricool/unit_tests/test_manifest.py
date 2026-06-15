# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for source-metricool manifest.yaml.

Validates the declarative manifest schema definitions.
"""

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def _get_schema(manifest, schema_name):
    return manifest["schemas"][schema_name]


@pytest.mark.parametrize(
    "field_name,expected_types",
    [
        pytest.param("url", ["string", "null"], id="url"),
        pytest.param("title", ["string", "null"], id="title"),
    ],
)
def test_brands_schema_contains_field(manifest, field_name, expected_types):
    """The brands schema must declare url and title as optional string fields."""
    schema = _get_schema(manifest, "brands")
    properties = schema["properties"]

    assert field_name in properties, f"brands schema is missing the '{field_name}' property"
    assert (
        properties[field_name]["type"] == expected_types
    ), f"brands.{field_name} should be {expected_types}, got {properties[field_name]['type']}"


def test_brands_schema_existing_fields_unchanged(manifest):
    """Verify existing brands fields are still present and unmodified."""
    schema = _get_schema(manifest, "brands")
    properties = schema["properties"]

    expected_existing = {
        "id": ["number", "null"],
        "description": ["string", "null"],
        "label": ["string", "null"],
        "deleted": ["boolean", "null"],
        "hash": ["string", "null"],
    }
    for field, expected_type in expected_existing.items():
        assert field in properties, f"brands schema is missing existing field '{field}'"
        assert (
            properties[field]["type"] == expected_type
        ), f"brands.{field} type changed: expected {expected_type}, got {properties[field]['type']}"
