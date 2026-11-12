# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

from pytest import MonkeyPatch, fixture


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))


@fixture(autouse=True)
def in_memory_request_cache(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
