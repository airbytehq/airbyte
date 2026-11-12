# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import importlib.util
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

SOURCE_FOLDER = Path("/airbyte/integration_code/source_declarative_manifest")
if not SOURCE_FOLDER.exists():
    SOURCE_FOLDER = Path(__file__).parent.parent
sys.path.append(str(SOURCE_FOLDER))


def _load_components() -> None:
    module_name = "source_declarative_manifest.components"
    spec = importlib.util.spec_from_file_location(module_name, SOURCE_FOLDER / "components.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module


def get_source(
    config: Mapping[str, Any],
    state: list[AirbyteStateMessage] | None = None,
    catalog: ConfiguredAirbyteCatalog | None = None,
) -> YamlDeclarativeSource:
    _load_components()
    return YamlDeclarativeSource(
        path_to_yaml=str(SOURCE_FOLDER / "manifest.yaml"),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )


@pytest.fixture(autouse=True)
def isolate_request_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    with freeze_time("2025-01-03T00:00:00Z"):
        yield
