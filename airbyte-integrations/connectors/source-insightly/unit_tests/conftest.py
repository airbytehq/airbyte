# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

MANIFEST_PATH = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
if not MANIFEST_PATH.exists():
    MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

REQUEST_CACHE_PATH = Path(__file__).parent / "REQUEST_CACHE_PATH"
os.environ["REQUEST_CACHE_PATH"] = str(REQUEST_CACHE_PATH)


def get_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config, catalog=catalog, state=[])


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    if REQUEST_CACHE_PATH.is_dir():
        for path in REQUEST_CACHE_PATH.glob("*.sqlite"):
            path.unlink()
