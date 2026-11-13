# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for source-zoho-books unit tests."""

from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    """Resolve the connector manifest for local and CI test layouts."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    return ci_path if ci_path.exists() else Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"


def get_source(config, state=None) -> YamlDeclarativeSource:
    """Instantiate a YamlDeclarativeSource using the Zoho Books manifest."""
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )
