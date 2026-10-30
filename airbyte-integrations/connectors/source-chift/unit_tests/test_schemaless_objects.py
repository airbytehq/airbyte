# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the two objects whose keys are defined by the integration, not by Chift's contract.

Chift's OpenAPI declares both objects free-form. On destinations that materialize declared
nested shapes (S3/GCS Avro and Parquet), a property that is not declared inside a declared
object is dropped silently, with nothing recorded in `_airbyte_meta.changes[]`. Both objects
below therefore have to stay schemaless, so the whole object survives as a JSON string.

These tests fail if a future edit re-introduces an enumerated property list.
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="module")
def schemas() -> dict:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())["schemas"]


@pytest.fixture(scope="module")
def connections_data(schemas: dict) -> dict:
    return schemas["connections"]["properties"]["data"]


@pytest.fixture(scope="module")
def display_condition(schemas: dict) -> dict:
    sub_mappings = schemas["syncs"]["properties"]["mappings"]["items"]["properties"]["sub_mappings"]
    return sub_mappings["items"]["properties"]["target_field"]["properties"]["display_condition"]


@pytest.mark.parametrize(
    "fixture_name, reason",
    [
        ("connections_data", "the connection payload differs per integration"),
        ("display_condition", "a condition expression tree has an open-ended operator set"),
    ],
)
def test_object_is_schemaless(fixture_name: str, reason: str, request) -> None:
    schema = request.getfixturevalue(fixture_name)

    assert "properties" not in schema, (
        f"`{fixture_name}` must stay schemaless because {reason}; enumerating its keys makes "
        f"schematizing destinations (S3/GCS Avro and Parquet) drop every key not listed. "
        f"Got: {sorted(schema.get('properties', {}))}"
    )
    assert "object" in schema["type"], f"expected an object type, got {schema['type']!r}"
