# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for incremental sync on `source-incident-io`.

Covers the `incidents`, `alerts` and `escalations` streams, which filter
server-side on the incident.io list endpoints via `updated_at[gte]` /
`created_at[gte]` and persist a datetime cursor.
"""

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"

_BASE_URL = "https://api.incident.io"

_CONFIG = {"api_key": "test_api_key", "start_date": "2024-01-01T00:00:00Z"}

_INCREMENTAL_STREAMS = {
    "incidents": ("updated_at", "updated_at%5Bgte%5D"),
    "alerts": ("created_at", "created_at%5Bgte%5D"),
    "escalations": ("updated_at", "updated_at%5Bgte%5D"),
}

_PATHS = {"incidents": "/v2/incidents", "alerts": "/v2/alerts", "escalations": "/v2/escalations"}


def _record(stream: str, record_id: str, cursor_value: str) -> dict:
    cursor_field = _INCREMENTAL_STREAMS[stream][0]
    return {"id": record_id, "created_at": cursor_value, "updated_at": cursor_value, cursor_field: cursor_value}


def _response(stream: str, records: list[dict], after: str | None = None) -> dict:
    return {stream: records, "pagination_meta": {"after": after, "page_size": 25}}


def _read_stream(stream: str, config: dict | None = None, state=None):
    config = config or _CONFIG
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return read(source, config, catalog, state)


@pytest.mark.parametrize("stream", list(_INCREMENTAL_STREAMS), ids=str)
def test_stream_supports_incremental(stream):
    """The stream advertises incremental sync and its cursor field in the catalog."""
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH), catalog=CatalogBuilder().build(), config=_CONFIG, state=StateBuilder().build()
    )
    declared = {s.name: s for s in source.discover(logger=None, config=_CONFIG).streams}
    cursor_field = _INCREMENTAL_STREAMS[stream][0]

    assert SyncMode.incremental in declared[stream].supported_sync_modes
    assert declared[stream].default_cursor_field == [cursor_field]


@pytest.mark.parametrize("stream", list(_INCREMENTAL_STREAMS), ids=str)
def test_start_date_is_sent_as_filter(stream):
    """The first sync filters server-side from the configured start_date."""
    _, encoded_param = _INCREMENTAL_STREAMS[stream]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{_PATHS[stream]}", json=_response(stream, []))
        _read_stream(stream)

    assert f"{encoded_param}=2024-01-01" in mocker.last_request.url


@pytest.mark.parametrize("stream", list(_INCREMENTAL_STREAMS), ids=str)
def test_state_is_used_as_filter(stream):
    """A subsequent sync resumes from the persisted cursor instead of start_date."""
    cursor_field, encoded_param = _INCREMENTAL_STREAMS[stream]
    state = StateBuilder().with_stream_state(stream, {cursor_field: "2024-06-15"}).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{_PATHS[stream]}", json=_response(stream, []))
        _read_stream(stream, state=state)

    assert f"{encoded_param}=2024-06-15" in mocker.last_request.url


@pytest.mark.parametrize("stream", list(_INCREMENTAL_STREAMS), ids=str)
def test_cursor_advances_to_latest_record(stream):
    """State is emitted with the highest cursor value seen in the sync."""
    cursor_field = _INCREMENTAL_STREAMS[stream][0]
    records = [_record(stream, "01A", "2024-03-01T10:00:00.000Z"), _record(stream, "01B", "2024-05-20T08:30:00.000Z")]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{_PATHS[stream]}", json=_response(stream, records))
        output = _read_stream(stream)

    assert [r.record.data["id"] for r in output.records] == ["01A", "01B"]
    assert output.most_recent_state.stream_state.__dict__[cursor_field] == "2024-05-20"


@pytest.mark.parametrize("stream", list(_INCREMENTAL_STREAMS), ids=str)
def test_incremental_stream_still_paginates(stream):
    """Adding the cursor does not break cursor-based pagination."""
    page1 = _response(stream, [_record(stream, "01A", "2024-03-01T10:00:00.000Z")], after="01A")
    page2 = _response(stream, [_record(stream, "01B", "2024-03-02T10:00:00.000Z")])

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}{_PATHS[stream]}",
            [{"json": page1, "status_code": 200}, {"json": page2, "status_code": 200}],
        )
        output = _read_stream(stream)

    assert [r.record.data["id"] for r in output.records] == ["01A", "01B"]


@pytest.mark.parametrize("stream", list(_INCREMENTAL_STREAMS), ids=str)
def test_start_date_defaults_when_not_configured(stream):
    """start_date is optional; syncs fall back to the default start datetime."""
    _, encoded_param = _INCREMENTAL_STREAMS[stream]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{_PATHS[stream]}", json=_response(stream, []))
        output = _read_stream(stream, config={"api_key": "test_api_key"})

    assert output.errors == []
    assert f"{encoded_param}=2020-01-01" in mocker.last_request.url


def test_full_refresh_streams_are_unchanged():
    """Streams without server-side timestamp filters stay full refresh."""
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH), catalog=CatalogBuilder().build(), config=_CONFIG, state=StateBuilder().build()
    )
    declared = {s.name: s for s in source.discover(logger=None, config=_CONFIG).streams}

    assert declared["users"].supported_sync_modes == [SyncMode.full_refresh]
    assert declared["severities"].supported_sync_modes == [SyncMode.full_refresh]
