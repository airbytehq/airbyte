# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture(autouse=True)
def isolate_request_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def get_source(config):
    manifest_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_folder.exists():
        manifest_folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(manifest_folder / "manifest.yaml"), config=config, catalog=CatalogBuilder().build()
    )
