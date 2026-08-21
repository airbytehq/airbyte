#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Tests for source-linear integration test configurations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import pytest
import yaml
from jsonschema import ValidationError, validate


CONNECTOR_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = CONNECTOR_DIR / "manifest.yaml"
INTEGRATION_TESTS_DIR = CONNECTOR_DIR / "integration_tests"
ACCEPTANCE_CONFIG_PATH = CONNECTOR_DIR / "acceptance-test-config.yml"
PATH_KEYS = {"config_path", "configured_catalog_path", "spec_path"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _load_manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _referenced_paths(value: Any) -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PATH_KEYS and isinstance(child, str):
                yield key, child
            yield from _referenced_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from _referenced_paths(child)


def test_authentication_sample_configs_select_distinct_schema_branches() -> None:
    manifest = _load_manifest()
    connection_specification = manifest["spec"]["connection_specification"]
    authentication_schemas = {
        schema["properties"]["auth_type"]["const"]: schema for schema in connection_specification["properties"]["credentials"]["oneOf"]
    }
    api_schema = authentication_schemas["API Key"]
    oauth_schema = authentication_schemas["OAuth2.0"]
    api_config = _load_json(INTEGRATION_TESTS_DIR / "sample_config.json")
    oauth_config = _load_json(INTEGRATION_TESTS_DIR / "sample_config_oauth.json")

    validate(api_config, connection_specification)
    validate(oauth_config, connection_specification)
    validate(api_config["credentials"], api_schema)
    validate(oauth_config["credentials"], oauth_schema)
    with pytest.raises(ValidationError):
        validate(api_config["credentials"], oauth_schema)
    with pytest.raises(ValidationError):
        validate(oauth_config["credentials"], api_schema)


def test_invalid_configs_are_schema_valid() -> None:
    connection_specification = _load_manifest()["spec"]["connection_specification"]

    validate(_load_json(INTEGRATION_TESTS_DIR / "invalid_config.json"), connection_specification)
    validate(_load_json(INTEGRATION_TESTS_DIR / "invalid_config_oauth.json"), connection_specification)


def test_acceptance_test_paths_are_available_locally_or_in_ci_secrets() -> None:
    acceptance_config = yaml.safe_load(ACCEPTANCE_CONFIG_PATH.read_text())

    assert "bypass_reason" not in json.dumps(acceptance_config)
    for key, configured_path in _referenced_paths(acceptance_config):
        path = Path(configured_path)
        if path.parts[:1] == ("secrets",):
            continue
        assert (CONNECTOR_DIR / path).is_file(), f"{key} does not exist: {configured_path}"


def test_catalogs_match_manifest_streams() -> None:
    manifest = _load_manifest()
    declared_streams = sorted(manifest["definitions"]["streams"])
    incremental_streams = sorted(name for name, stream in manifest["definitions"]["streams"].items() if "incremental_sync" in stream)
    configured_catalog = _load_json(INTEGRATION_TESTS_DIR / "configured_catalog.json")
    incremental_catalog = _load_json(INTEGRATION_TESTS_DIR / "incremental_catalog.json")
    configured_names = [entry["stream"]["name"] for entry in configured_catalog["streams"]]
    incremental_entries = incremental_catalog["streams"]
    incremental_names = [entry["stream"]["name"] for entry in incremental_entries]

    assert configured_names == declared_streams
    assert incremental_names == incremental_streams
    assert all(entry["sync_mode"] == "incremental" for entry in incremental_entries)
