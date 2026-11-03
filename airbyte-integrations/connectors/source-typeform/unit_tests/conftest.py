# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_folder() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_folder()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
_PACKAGE_NAME = "source_declarative_manifest"
_COMPONENT_MODULE_NAME = f"{_PACKAGE_NAME}.components"

sys.path.append(str(_SOURCE_FOLDER_PATH))

if _PACKAGE_NAME not in sys.modules:
    source_package = ModuleType(_PACKAGE_NAME)
    source_package.__path__ = [str(_SOURCE_FOLDER_PATH)]
    sys.modules[_PACKAGE_NAME] = source_package

component_spec = importlib.util.spec_from_file_location(_COMPONENT_MODULE_NAME, _SOURCE_FOLDER_PATH / "components.py")
if component_spec is None or component_spec.loader is None:
    raise ImportError(f"Could not load custom components from {_SOURCE_FOLDER_PATH / 'components.py'}")
component_module = importlib.util.module_from_spec(component_spec)
sys.modules[_COMPONENT_MODULE_NAME] = component_module
component_spec.loader.exec_module(component_module)
setattr(sys.modules[_PACKAGE_NAME], "components", component_module)


def get_source(config: Mapping[str, Any], state: Any = None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = state or StateBuilder().build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
