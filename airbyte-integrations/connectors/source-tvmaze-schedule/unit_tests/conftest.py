# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def get_source(config: dict, catalog: ConfiguredAirbyteCatalog, state: list[AirbyteStateMessage] | None = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parent.parent / "manifest.yaml"), config=config, catalog=catalog, state=state
    )


def read_stream(
    stream: str, mode: SyncMode = SyncMode.incremental, cursor: str | None = None, country: str | None = None, end: str = ""
) -> EntrypointOutput:
    config = {"start_date": "2024-01-01", "domestic_schedule_country_code": "GB"}
    if end:
        config["end_date"] = end
    if country is not None:
        config["web_schedule_country_code"] = country
    catalog = CatalogBuilder().with_stream(stream, mode).build()
    state = StateBuilder().with_stream_state(stream, {"airdate": cursor}).build() if cursor else []
    return read(get_source(config, catalog, state), config=config, catalog=catalog, state=state)


@pytest.fixture(autouse=True)
def frozen_time_and_cache() -> Iterator[None]:
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.exists():
        for path in cache_dir.glob("*.sqlite"):
            path.unlink()
    with freeze_time("2024-01-02T12:00:00Z"):
        yield


@pytest.fixture
def discovered_schemas() -> dict[str, dict]:
    config = {"start_date": "2024-01-01", "domestic_schedule_country_code": "GB"}
    output = discover(get_source(config, CatalogBuilder().build()), config=config)
    assert output.errors == []
    return {stream.name: stream.json_schema for stream in output.catalog.catalog.streams}


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker
