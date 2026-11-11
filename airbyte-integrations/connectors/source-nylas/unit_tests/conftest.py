# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@pytest.fixture
def config() -> dict:
    return {
        "api_key": "test-api-key",
        "api_server": "us",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-03T00:00:00Z",
    }


def get_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> YamlDeclarativeSource:
    ci_manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest = ci_manifest if ci_manifest.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest), config=config, catalog=catalog, state=[])
