# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest


@pytest.fixture
def manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    return ci_path if ci_path.exists() else Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(autouse=True)
def isolate_request_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
