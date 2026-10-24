#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
import yaml


@pytest.fixture(scope="module")
def manifest(manifest_path):
    with open(manifest_path, "r") as f:
        return yaml.safe_load(f)


def _get_cards_schema_properties(manifest: dict) -> dict:
    """Extract properties from the cards stream schema in the streams list."""
    for stream in manifest.get("streams", []):
        if isinstance(stream, dict) and stream.get("name") == "cards":
            schema = stream["schema_loader"]["schema"]
            return schema["properties"]
    raise AssertionError("cards stream not found in manifest streams list")


def _get_cards_definition_schema_properties(manifest: dict) -> dict:
    """Extract properties from the cards_stream definition schema."""
    cards_def = manifest["definitions"]["cards_stream"]
    schema = cards_def["schema_loader"]["schema"]
    return schema["properties"]


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("address", id="address_field"),
        pytest.param("locationName", id="locationName_field"),
    ],
)
def test_cards_stream_schema_has_location_fields(manifest, field_name):
    properties = _get_cards_schema_properties(manifest)
    assert field_name in properties, f"Field '{field_name}' missing from cards stream schema"
    assert properties[field_name]["type"] == ["null", "string"], f"Field '{field_name}' should be a nullable string"


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("address", id="address_field"),
        pytest.param("locationName", id="locationName_field"),
    ],
)
def test_cards_definition_schema_has_location_fields(manifest, field_name):
    properties = _get_cards_definition_schema_properties(manifest)
    assert field_name in properties, f"Field '{field_name}' missing from cards_stream definition schema"
    assert properties[field_name]["type"] == ["null", "string"], f"Field '{field_name}' should be a nullable string"
