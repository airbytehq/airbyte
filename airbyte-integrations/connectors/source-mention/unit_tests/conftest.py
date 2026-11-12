# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture
def config() -> dict[str, str]:
    return {"api_key": "test-mention-token", "stats_start_date": "2026-09-01T00:00:00Z"}


@pytest.fixture(autouse=True)
def isolate_request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
