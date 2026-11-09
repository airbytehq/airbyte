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


CONNECTOR_DIR = Path(__file__).resolve().parent.parent


def get_source(
    config: Mapping[str, Any], state: list[AirbyteStateMessage] | None = None, catalog: ConfiguredAirbyteCatalog | None = None
) -> YamlDeclarativeSource:
    module_name = "source_declarative_manifest.components"
    spec = importlib.util.spec_from_file_location(module_name, CONNECTOR_DIR / "components.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return YamlDeclarativeSource(path_to_yaml=str(CONNECTOR_DIR / "manifest.yaml"), config=config, state=state, catalog=catalog)


@pytest.fixture(autouse=True)
def isolated_sync(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    with freeze_time("2025-01-03T00:00:00Z"):
        yield
