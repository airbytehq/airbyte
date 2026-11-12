# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Mapping

from pytest import MonkeyPatch, fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


def get_source(config: Mapping[str, Any], state=None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_get_manifest_path() / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build() if state is None else state,
    )


@fixture(autouse=True)
def in_memory_request_cache(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
