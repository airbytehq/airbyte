# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-youtube-data` unit tests."""

from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    """Resolve the path to the connector's `manifest.yaml`."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"


def read_stream(stream_name: str, config: dict) -> EntrypointOutput:
    """Run a full refresh read of a single stream against the connector manifest."""
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog,
        config=config,
        state=state,
    )
    return read(source, config, catalog, state)
