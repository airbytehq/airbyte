# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture(autouse=True)
def request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def get_source(config: dict) -> YamlDeclarativeSource:
    folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not folder.exists():
        folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(folder / "manifest.yaml"), config=config)
