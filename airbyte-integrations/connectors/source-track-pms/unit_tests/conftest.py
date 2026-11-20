# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture(autouse=True)
def isolate_request_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
