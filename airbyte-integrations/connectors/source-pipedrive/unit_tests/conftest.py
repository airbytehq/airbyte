# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from typing import Any, Mapping

from pytest import fixture

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


def get_source(config: Mapping[str, Any], state=None) -> YamlDeclarativeSource:
    """Create a YamlDeclarativeSource instance with the given config."""
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


@fixture(autouse=True)
def in_memory_request_cache(monkeypatch):
    """Keep the CDK's HTTP request cache in memory during tests.

    With REQUEST_CACHE_PATH set, every stream opens a shared sqlite file that concurrent partitions
    (for example the four mailbox folders of `mailThreads`) write at the same time, which intermittently
    fails with `sqlite3.DatabaseError: file is not a database`. Unset, the cache is per-session and in memory.
    """
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    yield
