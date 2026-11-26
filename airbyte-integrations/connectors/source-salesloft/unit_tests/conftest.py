# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"
_CI_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
_SOURCE_PATH = _CI_PATH if _CI_PATH.exists() else Path(__file__).parent.parent
sys.path.append(str(_SOURCE_PATH))


def get_source(config: dict) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_SOURCE_PATH / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
