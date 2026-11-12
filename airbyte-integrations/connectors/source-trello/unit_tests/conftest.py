# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture
def source_factory(
    manifest_path: Path, components_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> Callable[[dict, ConfiguredAirbyteCatalog], ConcurrentDeclarativeSource]:
    monkeypatch.setitem(sys.modules, "source_declarative_manifest.components", components_module)

    def create_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> ConcurrentDeclarativeSource:
        return ConcurrentDeclarativeSource(
            source_config=yaml.safe_load(manifest_path.read_text()), config=config, catalog=catalog, state=[]
        )

    return create_source


@pytest.fixture
def http_mocker() -> None:
    pass
