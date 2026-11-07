# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_UNIT_TESTS_DIR = Path(__file__).parent
if str(_UNIT_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS_DIR))


@pytest.fixture(autouse=True)
def _isolated_request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Give each test an isolated request cache."""
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
