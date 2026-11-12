# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


def get_source(config):
    manifest_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_folder.exists():
        manifest_folder = Path(__file__).resolve().parents[2]
    return YamlDeclarativeSource(
        path_to_yaml=str(manifest_folder / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
