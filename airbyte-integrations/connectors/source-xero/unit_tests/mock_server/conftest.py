# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest
import yaml

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource


@pytest.fixture
def get_source(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Callable[..., ConcurrentDeclarativeSource]:
    connector_dir = Path(__file__).resolve().parents[2]
    package = ModuleType("source_declarative_manifest")
    package.__path__ = [str(connector_dir)]
    monkeypatch.setitem(sys.modules, "source_declarative_manifest", package)
    monkeypatch.delitem(sys.modules, "source_declarative_manifest.components", raising=False)
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))

    def create_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> ConcurrentDeclarativeSource:
        return ConcurrentDeclarativeSource(
            source_config=yaml.safe_load((connector_dir / "manifest.yaml").read_text()), config=config, catalog=catalog, state=[]
        )

    return create_source
