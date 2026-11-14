# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-linkly` unit tests."""

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE_URL = "https://api.linklyhq.com/api/v1"
WORKSPACES_URL = f"{BASE_URL}/workspaces"
CONVERSIONS_URL = f"{BASE_URL}/conversions"

API_KEY = "test-linkly-api-key"
START_DATE = "2026-09-01"
CONFIG = {"api_key": API_KEY, "start_date": START_DATE}


def workspace_url(workspace_id: int, endpoint: str) -> str:
    return f"{BASE_URL}/workspace/{workspace_id}/{endpoint}"


def _get_manifest_path() -> Path:
    """Resolve the directory holding the connector's `manifest.yaml`.

    In CI the connector is copied into `/airbyte/integration_code/source_declarative_manifest/`.
    Locally, tests run from the connector's `unit_tests/` directory, so the manifest lives
    one directory up.
    """
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"


def get_source(config: dict, state=None) -> YamlDeclarativeSource:
    """Instantiate a `YamlDeclarativeSource` for `source-linkly` using its manifest."""
    catalog = CatalogBuilder().build()
    state = state if state is not None else StateBuilder().build()
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog,
        config=config,
        state=state,
    )


def read_stream(
    stream_name: str,
    config: dict = CONFIG,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state=None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """Run the connector against a single stream with the given sync mode and optional state."""
    state = state if state is not None else []
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(source, config, catalog, state, expecting_exception=expecting_exception)


def query_params(request) -> dict:
    """Return the query parameters of a recorded request, preserving case."""
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


def requests_to(request_history, path: str) -> list:
    """Filter recorded requests down to the ones targeting `path`."""
    return [request for request in request_history if request.path == path]


def records(output: EntrypointOutput) -> list:
    """Return the data of every record emitted by a read."""
    return [message.record.data for message in output.records]
