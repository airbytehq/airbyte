# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping

import airbyte_cdk
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    """Get path to manifest.yaml, handling both CI and local environments."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))
if "source_declarative_manifest" not in sys.modules:
    source_declarative_manifest = ModuleType("source_declarative_manifest")
    source_declarative_manifest.__path__ = [str(_SOURCE_FOLDER_PATH)]
    sys.modules["source_declarative_manifest"] = source_declarative_manifest


def get_source(config: Mapping[str, Any], state: Any | None = None) -> YamlDeclarativeSource:
    """Create a YamlDeclarativeSource instance with the given config."""
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    path_to_yaml = os.path.relpath(_YAML_FILE_PATH, Path(airbyte_cdk.__file__).parent)
    return YamlDeclarativeSource(path_to_yaml=path_to_yaml, catalog=catalog, config=config, state=state)
