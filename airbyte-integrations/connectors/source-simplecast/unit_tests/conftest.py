# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@pytest.fixture
def source() -> YamlDeclarativeSource:
    ci_directory = Path("/airbyte/integration_code/source_declarative_manifest")
    manifest_directory = ci_directory if ci_directory.exists() else Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(manifest_directory / "manifest.yaml"))
