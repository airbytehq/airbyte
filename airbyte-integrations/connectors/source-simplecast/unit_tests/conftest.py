# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"

_SOURCE_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
if not _SOURCE_PATH.exists():
    _SOURCE_PATH = Path(__file__).parent.parent


def get_source(config, state=None):
    return YamlDeclarativeSource(
        path_to_yaml=str(_SOURCE_PATH / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for cache_file in cache_dir.glob("*.sqlite"):
            cache_file.unlink()
