# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")

_UNIT_TESTS_DIR = Path(__file__).parent
if str(_UNIT_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS_DIR))


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"api_key": "test-key"}
_BASE_URL = "https://api.incident.io"


def _get_source(state=None, config=None):
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config or _CONFIG,
        state=state if state is not None else StateBuilder().build(),
    )


def _read_stream(stream_name, sync_mode=SyncMode.full_refresh, state=None, config=None):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(_get_source(state, config), config or _CONFIG, catalog, state=state)
