# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

SOURCE_FOLDER = Path("/airbyte/integration_code/source_declarative_manifest")
if not SOURCE_FOLDER.exists():
    SOURCE_FOLDER = Path(__file__).parent.parent
sys.path.append(str(SOURCE_FOLDER))


def get_source(config, state=None):
    return YamlDeclarativeSource(
        path_to_yaml=str(SOURCE_FOLDER / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def isolate_request_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
