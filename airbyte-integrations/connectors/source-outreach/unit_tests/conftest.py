# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture(autouse=True)
def manifest_runtime(monkeypatch, tmp_path):
    package = ModuleType("source_declarative_manifest")
    package.__path__ = [str(Path(__file__).resolve().parent.parent)]
    monkeypatch.setitem(sys.modules, "source_declarative_manifest", package)
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.fixture
def config():
    return {
        "client_id": "test-client",
        "client_secret": "test-secret",
        "refresh_token": "refresh-0",
        "redirect_uri": "https://example.com/callback",
        "start_date": "2024-01-01T00:00:00Z",
    }
