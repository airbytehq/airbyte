# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def get_source(config):
    source_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_path.exists():
        source_path = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(source_path / "manifest.yaml"), config=config)


@pytest.fixture(autouse=True)
def in_memory_request_cache(monkeypatch):
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)


@pytest.fixture
def backoff_waits(monkeypatch):
    waits = []
    monkeypatch.setattr("time.sleep", lambda seconds: waits.append(seconds))
    return waits
