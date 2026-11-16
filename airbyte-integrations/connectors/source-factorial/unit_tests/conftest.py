# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest

from airbyte_cdk.models import AirbyteStateMessage
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"

_CI_SOURCE_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
_SOURCE_PATH = _CI_SOURCE_PATH if _CI_SOURCE_PATH.exists() else Path(__file__).parent.parent


def get_source(config: Mapping[str, Any], state: list[AirbyteStateMessage] | None = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_SOURCE_PATH / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or [],
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> Iterator[None]:
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
