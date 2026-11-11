# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def _get_manifest_folder() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    return ci_path if ci_path.exists() else Path(__file__).parent.parent


_SOURCE_FOLDER = _get_manifest_folder()
sys.path.append(str(_SOURCE_FOLDER))


@fixture
def source(config):
    return YamlDeclarativeSource(path_to_yaml=str(_SOURCE_FOLDER / "manifest.yaml"), config=config)


@fixture
def config():
    return {
        "client_id": "client",
        "client_secret": "secret",
        "refresh_token": "refresh",
        "redirect_uri": "https://example.com/callback",
        "start_date": "2024-01-01T00:00:00Z",
    }


@fixture(autouse=True)
def request_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
