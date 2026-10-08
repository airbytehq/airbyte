# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

REQUEST_CACHE_PATH = Path(__file__).parent / "REQUEST_CACHE_PATH"
os.environ.setdefault("REQUEST_CACHE_PATH", str(REQUEST_CACHE_PATH))

_CONNECTOR_DIR = Path(__file__).parent.parent
_MANIFEST_PATH = _CONNECTOR_DIR / "manifest.yaml"

if str(_CONNECTOR_DIR) not in sys.path:
    sys.path.append(str(_CONNECTOR_DIR))


def base_config(**overrides: Any) -> dict[str, Any]:
    config: dict[str, Any] = {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
        "user_agent": "airbyte:reddit-ads-sync:v1.0 (by /u/airbyte)",
        "ad_account_id": "a2_abc123",
        "start_time": "2026-09-23T00:00:00Z",
    }
    config.update(overrides)
    return config


def get_source(
    config: Mapping[str, Any] | None = None,
    catalog: ConfiguredAirbyteCatalog | None = None,
    state: list[AirbyteStateMessage] | None = None,
) -> YamlDeclarativeSource:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    manifest_path = ci_path / "manifest.yaml" if ci_path.exists() else _MANIFEST_PATH
    return YamlDeclarativeSource(
        path_to_yaml=str(manifest_path),
        catalog=catalog or CatalogBuilder().build(),
        config=config or base_config(),
        state=state if state is not None else StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    if REQUEST_CACHE_PATH.is_dir():
        for file_path in REQUEST_CACHE_PATH.glob("*.sqlite"):
            file_path.unlink()
    yield
