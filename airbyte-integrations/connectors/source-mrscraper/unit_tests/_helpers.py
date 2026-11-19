# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-mrscraper` unit tests."""

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


RESULTS_URL = "https://api.app.mrscraper.com/api/v1/results"
API_TOKEN = "test-api-token"
CONFIG = {"api_key": API_TOKEN}


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


def today() -> date:
    return datetime.now(timezone.utc).date()


def days_ago(days: int) -> str:
    return (today() - timedelta(days=days)).isoformat()


def get_source(config: dict, state=None) -> YamlDeclarativeSource:
    """Instantiate a `YamlDeclarativeSource` for `source-mrscraper` using its manifest."""
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )


def read_results(config: dict, sync_mode: SyncMode = SyncMode.full_refresh, state=None) -> EntrypointOutput:
    """Read the `results` stream with the given sync mode and optional state."""
    state = state if state is not None else []
    catalog = CatalogBuilder().with_stream("results", sync_mode).build()
    return read(get_source(config=config, state=state), config, catalog, state)


def page(records: list, page_number: int = 1, total_page: int = 1, page_size: int = 50) -> dict:
    """MrScraper's list envelope: records under `data`, pagination under `meta`."""
    return {
        "message": "Successful fetch",
        "data": records,
        "meta": {"page": page_number, "pageSize": page_size, "total": len(records), "totalPage": total_page},
    }


def result(result_id: str, created_at: str, **fields) -> dict:
    record = {
        "id": result_id,
        "createdAt": created_at,
        "userId": "00000000-0000-4000-8000-000000000001",
        "scraperId": None,
        "type": "Playground",
        "url": "https://www.scrapethissite.com/pages/simple/",
        "status": "Finished",
        "error": None,
        "tokenUsage": 1,
        "bandwidthUsage": None,
        "runtime": "1.234",
        "data": {"html": "<html></html>"},
        "htmlPath": None,
        "dataPath": None,
        "recordingPath": None,
        "screenshotPath": None,
        "sqlDeliveryStatus": None,
    }
    record.update(fields)
    return record


def query_params(request) -> dict:
    """Flatten a request's query string into a dict of single values."""
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


def record_ids(output: EntrypointOutput) -> list:
    return [message.record.data["id"] for message in output.records]
