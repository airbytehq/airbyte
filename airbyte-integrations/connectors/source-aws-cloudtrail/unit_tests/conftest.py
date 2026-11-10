# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest
import yaml

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


_CONNECTOR_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_CONNECTOR_DIR))
_package = ModuleType("source_declarative_manifest")
_package.__path__ = [str(_CONNECTOR_DIR)]
sys.modules["source_declarative_manifest"] = _package
_spec = importlib.util.spec_from_file_location("source_declarative_manifest.components", _CONNECTOR_DIR / "components.py")
_components = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _components
_spec.loader.exec_module(_components)


@pytest.fixture
def source_factory() -> Callable:
    class LocalSource(YamlDeclarativeSource):
        def _read_and_parse_yaml_file(self, path_to_yaml_file: str) -> dict:
            return yaml.safe_load(Path(path_to_yaml_file).read_text())

    def create_source(config: dict, catalog, state: list) -> YamlDeclarativeSource:
        kwargs = {"config": config, "catalog": catalog, "state": state}
        supported = inspect.signature(YamlDeclarativeSource).parameters
        return LocalSource(path_to_yaml=str(_CONNECTOR_DIR / "manifest.yaml"), **{k: v for k, v in kwargs.items() if k in supported})

    return create_source
