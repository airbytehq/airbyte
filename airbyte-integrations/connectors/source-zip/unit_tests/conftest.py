# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_UNIT_TESTS_DIR = Path(__file__).parent
if str(_UNIT_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS_DIR))


@pytest.fixture(autouse=True)
def _isolated_request_cache(tmp_path, monkeypatch):
    """Give every test its own HTTP response cache.

    The CDK builds each `DynamicSchemaLoader` retriever with `use_cache=True`. The cache is a shared
    sqlite store, on disk under `REQUEST_CACHE_PATH` or in memory for the whole process when the
    variable is unset. Without a per-test path, a schema read in one test is served from the cache
    in the next one, so the mocked response is never requested.
    """
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path / "request_cache"))
