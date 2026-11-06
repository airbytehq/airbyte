# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder

_CONNECTOR_DIR = Path(__file__).parent.parent
_CI_DIR = Path("/airbyte/integration_code/source_declarative_manifest")
if _CI_DIR.exists():
    _CONNECTOR_DIR = _CI_DIR

sys.path.append(str(_CONNECTOR_DIR))


def get_source(config):
    return YamlDeclarativeSource(path_to_yaml=str(_CONNECTOR_DIR / "manifest.yaml"), config=config, catalog=CatalogBuilder().build())
