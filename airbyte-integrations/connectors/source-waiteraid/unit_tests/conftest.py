# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.mock_http import HttpMocker


def get_source(config: dict) -> YamlDeclarativeSource:
    ci_manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest = ci_manifest if ci_manifest.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest), config=config)


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
