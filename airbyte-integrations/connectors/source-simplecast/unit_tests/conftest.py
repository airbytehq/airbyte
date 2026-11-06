# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def get_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> YamlDeclarativeSource:
    container_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest_path = container_path if container_path.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=config, catalog=catalog)


@pytest.fixture(autouse=True)
def isolate_request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    yield
    for cache_file in Path(os.environ["REQUEST_CACHE_PATH"]).glob("*.sqlite*"):
        cache_file.unlink()
