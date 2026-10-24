# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config, state=None):
    folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not folder.exists():
        folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(folder / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or [],
    )


@pytest.fixture(autouse=True)
def clear_cache():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
