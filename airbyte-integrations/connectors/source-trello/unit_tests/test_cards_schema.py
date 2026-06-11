#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def manifest():
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())


def _get_cards_schema_from_definitions(manifest):
    return manifest["definitions"]["cards_stream"]["schema_loader"]["schema"]["properties"]


def _get_cards_schema_from_streams(manifest):
    streams = manifest["streams"]
    cards_stream = next(s for s in streams if s.get("name") == "cards")
    return cards_stream["schema_loader"]["schema"]["properties"]


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("address", id="address_field"),
        pytest.param("locationName", id="locationName_field"),
    ],
)
def test_cards_schema_definitions_contains_location_fields(manifest, field_name):
    schema_properties = _get_cards_schema_from_definitions(manifest)
    assert field_name in schema_properties, f"Field '{field_name}' missing from cards schema in definitions section"
    assert schema_properties[field_name]["type"] == ["null", "string"]


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("address", id="address_field"),
        pytest.param("locationName", id="locationName_field"),
    ],
)
def test_cards_schema_streams_contains_location_fields(manifest, field_name):
    schema_properties = _get_cards_schema_from_streams(manifest)
    assert field_name in schema_properties, f"Field '{field_name}' missing from cards schema in streams section"
    assert schema_properties[field_name]["type"] == ["null", "string"]
