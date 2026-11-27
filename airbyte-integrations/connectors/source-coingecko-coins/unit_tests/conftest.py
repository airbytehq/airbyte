# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from airbyte_cdk.models import AirbyteStateMessage
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config: dict, state: list[AirbyteStateMessage] | None = None) -> YamlDeclarativeSource:
    source_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_path.exists():
        source_path = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(source_path / "manifest.yaml"), config=config, state=state, catalog=CatalogBuilder().build()
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> Iterator[None]:
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    for path in cache_dir.glob("*.sqlite"):
        path.unlink()
    yield
