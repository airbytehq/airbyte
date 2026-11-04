# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import (
    YamlDeclarativeSource,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker


def get_source(config):
    manifest_dir = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_dir.exists():
        manifest_dir = Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(manifest_dir / "manifest.yaml"),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )
