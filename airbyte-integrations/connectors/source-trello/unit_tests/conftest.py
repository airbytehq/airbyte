# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def _get_manifest_folder() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_folder()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.insert(0, str(_SOURCE_FOLDER_PATH))


@pytest.fixture
def http_mocker() -> None:
    """Provide the parameter injected by the HttpMocker decorator."""


def get_source(config, state=None):
    from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
    from airbyte_cdk.test.catalog_builder import CatalogBuilder
    from airbyte_cdk.test.state_builder import StateBuilder

    catalog = CatalogBuilder().build()
    state = state or StateBuilder().build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
