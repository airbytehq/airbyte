# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config, state=None):
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest_path = ci_path if ci_path.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config, catalog=CatalogBuilder().build(), state=state)


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    for cache_file in cache_dir.glob("*.sqlite"):
        cache_file.unlink()
