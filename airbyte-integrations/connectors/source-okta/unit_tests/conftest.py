# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest

from airbyte_cdk.models import AirbyteStateMessage
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config: dict, state: list[AirbyteStateMessage] | None = None) -> YamlDeclarativeSource:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest = ci_path if ci_path.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest), config=config, catalog=CatalogBuilder().build(), state=state or [])


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    for cache in Path(os.environ["REQUEST_CACHE_PATH"]).glob("*.sqlite"):
        cache.unlink()
