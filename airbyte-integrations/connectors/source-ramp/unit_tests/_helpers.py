# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-ramp` unit tests."""

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE_URL = "https://api.ramp.com/developer/v1"
TOKEN_URL = f"{BASE_URL}/token"
CARDS_URL = f"{BASE_URL}/cards"
TRANSACTIONS_URL = f"{BASE_URL}/transactions"
REIMBURSEMENTS_URL = f"{BASE_URL}/reimbursements"

ACCESS_TOKEN = "test-access-token"
TOKEN_RESPONSE = {"access_token": ACCESS_TOKEN, "expires_in": 864000, "token_type": "Bearer"}

START_DATE = "2024-01-01T00:00:00Z"
CONFIG = {
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "start_date": START_DATE,
}


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
    """Instantiate a `YamlDeclarativeSource` for `source-ramp` using its manifest."""
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
) -> EntrypointOutput:
    """Run the connector against a single stream with the given sync mode and optional state."""
    state = state if state is not None else []
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(source, config, catalog, state)


def query_params(request) -> dict:
    """Return the query parameters of a recorded request, preserving case.

    `requests_mock` exposes `request.qs`, but it lowercases both keys and values, which would
    hide casing regressions in values such as `direction=BUSINESS_TO_USER`.
    """
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


def requests_to(request_history, path: str) -> list:
    """Filter recorded requests down to the ones targeting `path`."""
    return [request for request in request_history if request.path == path]


def record_ids(output: EntrypointOutput) -> list:
    """Return the `id` of every record emitted by a read."""
    return [message.record.data["id"] for message in output.records]
