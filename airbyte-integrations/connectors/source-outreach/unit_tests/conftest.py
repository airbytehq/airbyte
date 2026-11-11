# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_SOURCE_FOLDER = Path("/airbyte/integration_code/source_declarative_manifest")
if not _SOURCE_FOLDER.exists():
    _SOURCE_FOLDER = Path(__file__).parent.parent
sys.path.append(str(_SOURCE_FOLDER))


@pytest.fixture
def source(config):
    return YamlDeclarativeSource(path_to_yaml=str(_SOURCE_FOLDER / "manifest.yaml"), config=config)


@pytest.fixture(autouse=True)
def disable_retry_sleep(monkeypatch, tmp_path):
    monkeypatch.setattr("time.sleep", lambda _: None)
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
