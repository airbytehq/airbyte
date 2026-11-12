# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture(autouse=True)
def request_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def get_source(config, catalog):
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest = ci_path if ci_path.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest), config=config, catalog=catalog, state=[])
