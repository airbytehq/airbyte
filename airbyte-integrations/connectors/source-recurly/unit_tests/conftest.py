# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"
SOURCE_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
if not SOURCE_PATH.exists():
    SOURCE_PATH = Path(__file__).parent.parent
sys.path.append(str(SOURCE_PATH))


def get_source(config: dict, state: list | None = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(SOURCE_PATH / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or [],
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> Iterator[None]:
    for path in Path(os.environ["REQUEST_CACHE_PATH"]).glob("*.sqlite"):
        path.unlink()
    yield
