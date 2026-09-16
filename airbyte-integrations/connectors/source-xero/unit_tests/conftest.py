# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
import types
from pathlib import Path
from typing import Any, Mapping

import yaml

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))
source_declarative_manifest = types.ModuleType("source_declarative_manifest")
source_declarative_manifest.__path__ = [str(_SOURCE_FOLDER_PATH)]
sys.modules.setdefault("source_declarative_manifest", source_declarative_manifest)


class TestYamlDeclarativeSource(YamlDeclarativeSource):
    def _read_and_parse_yaml_file(self, path_to_yaml_file: str):
        return yaml.safe_load(Path(path_to_yaml_file).read_text())


def get_source(config: Mapping[str, Any], catalog=None) -> TestYamlDeclarativeSource:
    return TestYamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )
