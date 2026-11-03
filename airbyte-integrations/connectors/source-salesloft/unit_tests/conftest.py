# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

import yaml
from pytest import fixture

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"

_CI_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
_SOURCE_FOLDER_PATH = _CI_PATH if _CI_PATH.exists() else Path(__file__).parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))
_PACKAGE_NAME = "source_declarative_manifest"
_package = ModuleType(_PACKAGE_NAME)
_package.__path__ = [str(_SOURCE_FOLDER_PATH)]
sys.modules[_PACKAGE_NAME] = _package
_spec = spec_from_file_location(f"{_PACKAGE_NAME}.components", _SOURCE_FOLDER_PATH / "components.py")
_components = module_from_spec(_spec)
sys.modules[_spec.name] = _components
_spec.loader.exec_module(_components)


def get_source() -> ManifestDeclarativeSource:
    return ManifestDeclarativeSource(source_config=yaml.safe_load(_YAML_FILE_PATH.read_text()))


@fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
