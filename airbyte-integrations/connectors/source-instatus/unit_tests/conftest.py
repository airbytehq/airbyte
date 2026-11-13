# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_SOURCE_FOLDER_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
if not _SOURCE_FOLDER_PATH.exists():
    _SOURCE_FOLDER_PATH = Path(__file__).parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))


def get_source(config: Mapping[str, Any], catalog: Optional[ConfiguredAirbyteCatalog] = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )
