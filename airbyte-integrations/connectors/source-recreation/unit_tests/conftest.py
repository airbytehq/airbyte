# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from airbyte_cdk.models import AirbyteStateMessage
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.mock_http import HttpMocker


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config: dict, state: list[AirbyteStateMessage] | None = None) -> YamlDeclarativeSource:
    ci_manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    manifest = ci_manifest if ci_manifest.exists() else Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(path_to_yaml=str(manifest), config=config, state=state)


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> None:
    cache = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache.is_dir():
        for file in cache.glob("*.sqlite"):
            file.unlink()


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
