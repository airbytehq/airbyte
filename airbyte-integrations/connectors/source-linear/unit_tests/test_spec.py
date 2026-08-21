#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Unit tests for the source-linear connection specification."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")


def _credential_branches() -> Mapping[str, Mapping[str, Any]]:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config={})
    specification = source.spec(None)
    credentials = specification.connectionSpecification["properties"]["credentials"]

    return {branch["properties"]["auth_type"]["const"]: branch for branch in credentials["oneOf"]}


def test_credential_properties_have_titles_and_descriptions() -> None:
    branches = _credential_branches()

    assert set(branches) == {"API Key", "OAuth2.0"}
    for branch in branches.values():
        for property_name, property_schema in branch["properties"].items():
            assert property_schema.get("title"), f"{property_name} must have a title"
            if property_name != "auth_type":
                assert property_schema.get("description"), f"{property_name} must have a description"


def test_api_key_description_points_to_personal_api_keys() -> None:
    api_key_description = _credential_branches()["API Key"]["properties"]["api_key"]["description"]

    assert "Security & access" in api_key_description
    assert "Personal API keys" in api_key_description
    assert "Settings → API." not in api_key_description


def test_oauth_descriptions_explain_where_values_come_from() -> None:
    oauth_properties = _credential_branches()["OAuth2.0"]["properties"]

    for property_name in ("client_id", "client_secret", "refresh_token"):
        description = oauth_properties[property_name]["description"]
        assert description != oauth_properties[property_name]["title"]

    assert "Applications" in oauth_properties["client_id"]["description"]
    assert "Applications" in oauth_properties["client_secret"]["description"]
    assert "OAuth" in oauth_properties["refresh_token"]["description"]
    assert "flow" in oauth_properties["refresh_token"]["description"]
