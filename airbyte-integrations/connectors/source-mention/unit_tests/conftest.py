# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@pytest.fixture
def config():
    return {"api_key": "test-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}


@pytest.fixture
def source(config):
    manifest_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_folder.exists():
        manifest_folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(manifest_folder / "manifest.yaml"), config=config)
