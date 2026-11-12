# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config):
    source_dir = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_dir.exists():
        source_dir = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(source_dir / "manifest.yaml"),
        config=config,
        catalog=CatalogBuilder().build(),
        state=[],
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker
