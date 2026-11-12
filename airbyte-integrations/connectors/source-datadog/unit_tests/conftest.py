# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
CONFIG = {"api_key": "fake-api-key", "application_key": "fake-application-key", "site": "datadoghq.com"}


def get_source(
    config: Mapping[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
    catalog: ConfiguredAirbyteCatalog | None = None,
) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(MANIFEST_PATH),
        catalog=catalog,
        config=CONFIG if config is None else config,
        state=state,
    )


def read_stream(
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    config: Mapping[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
) -> EntrypointOutput:
    """Read one stream. The caller mocks the HTTP responses."""
    config = CONFIG if config is None else config
    stream = ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(sync_mode)
    catalog = CatalogBuilder().with_stream(stream).build()
    return read(get_source(config, state, catalog), config, catalog, state)
