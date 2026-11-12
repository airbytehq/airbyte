# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def get_source(config: dict) -> YamlDeclarativeSource:
    source_dir = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_dir.exists():
        source_dir = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(source_dir / "manifest.yaml"),
        config=config,
        catalog=CatalogBuilder().build(),
        state=[],
    )


@pytest.fixture(autouse=True)
def isolate_request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
