# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
