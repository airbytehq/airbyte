#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


# Cached HTTP sessions (dynamic schema loaders force `use_cache=True`) fall back to one
# in-memory SQLite database shared by the whole process, which outlives any test that leaves a
# session open: one test's cached metadata responses then satisfy a later test's requests, and
# that test observes no request at all. Giving each test its own cache directory isolates them.
@pytest.fixture(autouse=True)
def isolated_http_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    yield


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def get_source(config, state=None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )
