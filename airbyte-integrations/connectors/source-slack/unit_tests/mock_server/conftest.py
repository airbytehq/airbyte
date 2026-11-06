# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest


@pytest.fixture(autouse=True)
def isolated_request_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
