# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")


def _get_manifest_path() -> Path:
    """Find the connector directory holding manifest.yaml.

    In CI (Docker): /airbyte/integration_code/source_declarative_manifest
    Locally: the connector root, one level above unit_tests/
    """
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    # .resolve() because __file__ may be relative in CI.
    return Path(__file__).resolve().parent.parent


MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"


def get_source(config, state=None) -> YamlDeclarativeSource:
    """Build the declarative source under test from the connector's manifest.yaml."""
    return YamlDeclarativeSource(
        path_to_yaml=str(MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )
