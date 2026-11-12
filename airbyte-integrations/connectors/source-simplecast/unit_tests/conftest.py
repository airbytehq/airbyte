# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture(autouse=True)
def request_cache_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def get_source(config: dict) -> YamlDeclarativeSource:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    manifest_dir = ci_path if ci_path.exists() else Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(manifest_dir / "manifest.yaml"), config=config)
