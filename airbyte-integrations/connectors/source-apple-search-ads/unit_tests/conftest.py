# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
import time
from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")

_UNIT_TESTS_DIR = Path(__file__).parent
if str(_UNIT_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS_DIR))


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Record backoff waits instead of sleeping through them."""
    calls = []
    monkeypatch.setattr(time, "sleep", calls.append)
    return calls
