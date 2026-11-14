# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
import types

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture
def get_source(manifest_path, monkeypatch, tmp_path):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    package = types.ModuleType("source_declarative_manifest")
    package.__path__ = [str(manifest_path.parent)]
    monkeypatch.setitem(sys.modules, "source_declarative_manifest", package)
    monkeypatch.delitem(sys.modules, "source_declarative_manifest.components", raising=False)

    def create(config, catalog, state=None):
        return YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config, catalog=catalog, state=state)

    return create
