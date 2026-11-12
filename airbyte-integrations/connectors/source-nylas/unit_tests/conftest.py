# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


@pytest.fixture(autouse=True)
def isolate_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.fixture
def config() -> dict:
    return {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }


def read_stream(config: dict, stream: str = "events", sync_mode: SyncMode = SyncMode.full_refresh) -> EntrypointOutput:
    ci_manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest = ci_manifest if ci_manifest.exists() else Path(__file__).parent.parent / "manifest.yaml"
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest), config=config, catalog=catalog)
    return read(source, config=config, catalog=catalog)
