# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from types import ModuleType

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture
def source_builder(manifest_path, request, monkeypatch):
    def build(**kwargs) -> YamlDeclarativeSource:
        source = YamlDeclarativeSource(str(manifest_path), **kwargs)
        components = request.getfixturevalue("components_module")
        package = ModuleType("source_declarative_manifest")
        package.components = components
        monkeypatch.setitem(sys.modules, "source_declarative_manifest", package)
        monkeypatch.setitem(sys.modules, "source_declarative_manifest.components", components)
        return source

    return build
