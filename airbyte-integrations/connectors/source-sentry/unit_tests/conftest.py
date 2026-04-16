# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


# Load CDK's manifest-only test fixtures
pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

# Set up request cache path
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def _get_manifest_path() -> Path:
    """
    Find manifest.yaml location.

    In CI (Docker): /airbyte/integration_code/source_declarative_manifest/manifest.yaml
    Locally: ../manifest.yaml (relative to unit_tests/)
    """
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent  # Local: parent of unit_tests/


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

# Add to path to allow importing custom components (if you have components.py)
sys.path.append(str(_SOURCE_FOLDER_PATH))


def get_source(config, state=None) -> YamlDeclarativeSource:
    """
    Create a YamlDeclarativeSource instance for testing.

    This is the main entry point for running your connector in tests.
    """
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


@fixture(autouse=True)
def clear_cache_before_each_test():
    """
    CRITICAL: Clear request cache before each test!

    Without this, cached responses from one test will affect other tests.
    """
    cache_dir = Path(os.getenv("REQUEST_CACHE_PATH"))
    if cache_dir.exists() and cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield  # Test runs here
