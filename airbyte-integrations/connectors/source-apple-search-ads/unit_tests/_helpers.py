# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-apple-search-ads` unit tests."""

from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


def _get_connector_dir() -> Path:
    """Resolve the connector directory containing `manifest.yaml`."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_connector_dir() / "manifest.yaml"


def get_source(
    config: Mapping[str, Any],
    catalog: Optional[ConfiguredAirbyteCatalog] = None,
    state=None,
) -> YamlDeclarativeSource:
    """Instantiate a `YamlDeclarativeSource` for `source-apple-search-ads`."""
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )
