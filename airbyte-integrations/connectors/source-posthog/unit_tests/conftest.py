# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest


@pytest.fixture(autouse=True)
def isolated_request_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
