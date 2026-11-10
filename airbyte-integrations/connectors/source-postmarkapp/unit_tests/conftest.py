# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent / "manifest.yaml"


def get_source(config, state=None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_get_manifest_path()),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )


@fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
