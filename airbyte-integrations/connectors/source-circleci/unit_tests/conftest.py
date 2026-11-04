# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from collections.abc import Iterator
from pathlib import Path

import yaml
from pytest import MonkeyPatch, fixture

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def _get_manifest_path() -> Path:
    """Get path to manifest.yaml, handling both CI and local environments."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))


def get_source() -> ManifestDeclarativeSource:
    return ManifestDeclarativeSource(yaml.safe_load(_YAML_FILE_PATH.read_text()))


@fixture(autouse=True)
def in_memory_request_cache(monkeypatch: MonkeyPatch) -> Iterator[None]:
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    yield
