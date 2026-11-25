# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-zip` unit tests."""

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE_URL = "https://api.ziphq.com"
REQUESTS_URL = f"{BASE_URL}/requests"
PURCHASE_ORDERS_URL = f"{BASE_URL}/purchase_orders"
INVOICES_URL = f"{BASE_URL}/invoices"

REQUESTS_PATH = "/requests"
PURCHASE_ORDERS_PATH = "/purchase_orders"
INVOICES_PATH = "/invoices"

API_KEY = "test-zip-api-key"
API_VERSION = "2024-06-06"
START_DATE = "2024-01-01T00:00:00Z"
START_DATE_EPOCH = "1704067200"
DEFAULT_START_DATE_EPOCH = "1577836800"  # 2020-01-01T00:00:00Z

CONFIG = {
    "api_key": API_KEY,
    "api_version": API_VERSION,
    "start_date": START_DATE,
}

# Every stream shares the same cursor shape; only the filter name and the page size differ.
STREAMS = {
    "requests": {"url": REQUESTS_URL, "path": REQUESTS_PATH, "filter": "last_updated_after", "page_size": "30"},
    "purchase_orders": {"url": PURCHASE_ORDERS_URL, "path": PURCHASE_ORDERS_PATH, "filter": "last_updated_after", "page_size": "50"},
    "invoices": {"url": INVOICES_URL, "path": INVOICES_PATH, "filter": "updated_after", "page_size": "50"},
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
    """Instantiate a `YamlDeclarativeSource` for `source-zip` using its manifest."""
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


def page(records: list, next_page_token=None) -> dict:
    """Zip's list envelope: records under `list`, the cursor under `next_page_token`."""
    body = {"list": records, "size": len(records), "total": len(records) or None}
    if next_page_token is not None:
        body["next_page_token"] = next_page_token
    return body


def record(record_id: str, updated_at: int, **extra) -> dict:
    """A minimal Zip record. Zip returns every key on every record, null when unset."""
    base = {
        "id": record_id,
        "name": f"Record {record_id}",
        "status": 1,
        "amount_usd": "1250.00",
        "vendor": {"id": "vendor-1", "name": "Vendor"},
        "attributes": [{"name": "Campaign", "value": "Q3 Launch"}],
        "created_at": updated_at - 3600,
        "updated_at": updated_at,
        "description": None,
    }
    base.update(extra)
    return base


def config_without(*keys: str) -> dict:
    """CONFIG with the given keys removed, to test the manifest's defaults."""
    return {key: value for key, value in CONFIG.items() if key not in keys}


def sync_url(stream_name: str, cursor: str) -> str:
    """The stream's URL with the filter parameter every sync request carries."""
    stream = STREAMS[stream_name]
    return f"{stream['url']}?{stream['filter']}={cursor}"


def sync_requests(request_history, stream_name: str) -> list:
    """Recorded requests to the stream's endpoint that carry the incremental filter (the sync)."""
    stream = STREAMS[stream_name]
    return [request for request in requests_to(request_history, stream["path"]) if stream["filter"] in query_params(request)]


def schema_requests(request_history, stream_name: str) -> list:
    """Recorded requests to the stream's endpoint without the filter (the schema loader's read)."""
    stream = STREAMS[stream_name]
    return [request for request in requests_to(request_history, stream["path"]) if stream["filter"] not in query_params(request)]


def mock_schema_read(mocker, stream_name: str) -> None:
    """Serve the schema loader's unfiltered read with one record."""
    mocker.get(STREAMS[stream_name]["url"], json=page([record("schema-1", 1718000500)]))


def stream_schema(stream_name: str, config: dict = CONFIG) -> dict:
    """The merged JSON schema the connector declares for a stream."""
    return next(stream for stream in get_source(config).streams(config) if stream.name == stream_name).get_json_schema()


def query_params(request) -> dict:
    """Return the query parameters of a recorded request, preserving case."""
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


def requests_to(request_history, path: str) -> list:
    """Filter recorded requests down to the ones targeting `path`."""
    return [request for request in request_history if request.path == path]


def record_ids(output: EntrypointOutput) -> list:
    """Return the `id` of every record emitted by a read."""
    return [message.record.data["id"] for message in output.records]
