# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@pytest.fixture(autouse=True)
def request_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def get_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> YamlDeclarativeSource:
    source_dir = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_dir.exists():
        source_dir = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(source_dir / "manifest.yaml"), config=config, catalog=catalog)
