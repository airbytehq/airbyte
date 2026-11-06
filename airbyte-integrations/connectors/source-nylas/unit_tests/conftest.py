# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Mapping, Optional

import pytest

from airbyte_cdk.models import AirbyteStateMessage
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


def get_source(config: Mapping[str, Any], state: Optional[list[AirbyteStateMessage]] = None) -> YamlDeclarativeSource:
    source_dir = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_dir.exists():
        source_dir = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(source_dir / "manifest.yaml"),
        config=config,
        catalog=CatalogBuilder().build(),
        state=state or [],
    )


@pytest.fixture
def config() -> dict[str, str]:
    return {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }


@pytest.fixture(autouse=True)
def in_memory_request_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
