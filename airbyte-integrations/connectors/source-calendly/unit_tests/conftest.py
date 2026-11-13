# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path
from typing import Any, Mapping

from freezegun import freeze_time
from pytest import MonkeyPatch, fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = Path(os.environ.get("CALENDLY_MANIFEST_PATH", _SOURCE_FOLDER_PATH / "manifest.yaml"))
sys.path.append(str(_SOURCE_FOLDER_PATH))


def get_source(config: Mapping[str, Any], state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if state is None else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


@fixture(autouse=True)
def in_memory_request_cache(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)


@fixture
def recorded_sleeps(monkeypatch: MonkeyPatch):
    sleeps = []
    with freeze_time("2024-02-01T00:00:00Z") as clock:

        def sleep(seconds: float) -> None:
            sleeps.append(seconds)
            # The extra millisecond steps past pyrate-limiter's inclusive window edge, as real time would.
            clock.tick(seconds + 0.001)

        monkeypatch.setattr("time.sleep", sleep)
        yield sleeps
