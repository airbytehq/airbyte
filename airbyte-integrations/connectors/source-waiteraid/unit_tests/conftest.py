# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@pytest.fixture
def config():
    return {"start_date": "2026-09-03", "auth_hash": "test-auth-hash", "restid": "test-restaurant"}


@pytest.fixture
def source(config, tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    manifest_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_folder.exists():
        manifest_folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(manifest_folder / "manifest.yaml"), config=config)
