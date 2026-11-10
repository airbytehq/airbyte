# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_SOURCE_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
if not _SOURCE_PATH.exists():
    _SOURCE_PATH = Path(__file__).parent.parent
sys.path.append(str(_SOURCE_PATH))


@pytest.fixture(autouse=True)
def request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def get_source(config: dict[str, str]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_SOURCE_PATH / "manifest.yaml"), config=config, catalog=CatalogBuilder().build(), state=[]
    )
