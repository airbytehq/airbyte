# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker


# components.py is loaded by the manifest as `source_declarative_manifest.components`.
SOURCE_FOLDER = Path("/airbyte/integration_code/source_declarative_manifest")
if not SOURCE_FOLDER.exists():
    SOURCE_FOLDER = Path(__file__).parent.parent
sys.path.append(str(SOURCE_FOLDER))


@pytest.fixture(autouse=True)
def frozen_time() -> Iterator[None]:
    with freeze_time("2026-11-12T00:00:00Z"):
        yield


@pytest.fixture(autouse=True)
def isolate_request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
