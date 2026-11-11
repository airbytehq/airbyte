import pytest


@pytest.fixture(autouse=True)
def mock_auth():
    yield


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
