# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-grafana manifest.yaml.

Validates that the datasources stream schema includes all expected fields
returned by the Grafana Data Source HTTP API.
"""

import pathlib

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _get_datasources_schema_properties(manifest):
    for stream in manifest["streams"]:
        if stream["name"] == "datasources":
            return stream["schema_loader"]["schema"]["properties"]
    raise ValueError("datasources stream not found in manifest")


@pytest.mark.parametrize(
    "field_name,expected_types",
    [
        pytest.param("id", ["integer"], id="id"),
        pytest.param("uid", ["string", "null"], id="uid"),
        pytest.param("name", ["string", "null"], id="name"),
        pytest.param("type", ["string", "null"], id="type"),
        pytest.param("url", ["string", "null"], id="url"),
        pytest.param("user", ["string", "null"], id="user"),
        pytest.param("orgId", ["integer", "null"], id="orgId"),
        pytest.param("access", ["string", "null"], id="access"),
        pytest.param("database", ["string", "null"], id="database"),
        pytest.param("jsonData", ["object", "null"], id="jsonData"),
        pytest.param("readOnly", ["boolean", "null"], id="readOnly"),
        pytest.param("typeName", ["string", "null"], id="typeName"),
        pytest.param("basicAuth", ["boolean", "null"], id="basicAuth"),
        pytest.param("isDefault", ["boolean", "null"], id="isDefault"),
        pytest.param("typeLogoUrl", ["string", "null"], id="typeLogoUrl"),
        pytest.param("withCredentials", ["boolean", "null"], id="withCredentials"),
        pytest.param("secureJsonFields", ["object", "null"], id="secureJsonFields"),
        pytest.param("version", ["integer", "null"], id="version"),
    ],
)
def test_datasources_schema_has_field(manifest, field_name, expected_types):
    """Each expected Grafana datasource API field must be present with correct types."""
    props = _get_datasources_schema_properties(manifest)
    assert field_name in props, f"datasources schema is missing field '{field_name}'"
    actual_type = props[field_name]["type"]
    if isinstance(actual_type, str):
        actual_type = [actual_type]
    assert actual_type == expected_types, f"datasources field '{field_name}' has type {actual_type}, expected {expected_types}"


def test_datasources_primary_key_is_id(manifest):
    """The datasources stream primary key must be 'id'."""
    for stream in manifest["streams"]:
        if stream["name"] == "datasources":
            assert stream["primary_key"] == ["id"]
            return
    raise ValueError("datasources stream not found in manifest")
