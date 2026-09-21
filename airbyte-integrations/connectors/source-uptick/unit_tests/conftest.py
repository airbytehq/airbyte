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

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")


def _manifest_dir() -> Path:
    """In CI the connector is copied to `/airbyte/integration_code/source_declarative_manifest`."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _manifest_dir() / "manifest.yaml"

if str(_manifest_dir()) not in sys.path:
    sys.path.append(str(_manifest_dir()))


def base_config(**overrides: Any) -> dict[str, Any]:
    config: dict[str, Any] = {
        "base_url": "https://demo.onuptick.com",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "username": "user@example.com",
        "password": "password",
    }
    config.update(overrides)
    return config


def get_source(
    config: Mapping[str, Any],
    catalog: ConfiguredAirbyteCatalog | None = None,
    state: list[AirbyteStateMessage] | None = None,
) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """Clear the HTTP request cache so cached responses do not leak between tests."""
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for file_path in cache_dir.glob("*.sqlite"):
            file_path.unlink()
    yield
