# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import pytest
import requests_mock
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST = Path(__file__).resolve().parents[1] / "manifest.yaml"
if not MANIFEST.exists():
    MANIFEST = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
BASE_URL = "https://api.mailersend.com/v1/activity/test-domain"
CONFIG = {"api_token": "test-token", "domain_id": "test-domain", "start_date": 1788220800}


def read_activity(state: list[AirbyteStateMessage] | None = None, mode: SyncMode = SyncMode.incremental) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("activity", mode).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog, state=state)
    return read(source, CONFIG, catalog, state)


def mock_activity(http: requests_mock.Mocker, start: int, end: int, records: list[dict[str, str]]) -> None:
    query = urlencode({"limit": 100, "page_size": 100, "date_from": start, "date_to": end})
    http.get(
        f"{BASE_URL}?{query}",
        complete_qs=True,
        request_headers={"Authorization": "Bearer test-token"},
        json={"data": records},
    )


@freeze_time("2026-09-03T12:00:00Z")
@pytest.mark.parametrize("mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_activity_sends_both_bounds_for_every_daily_slice(mode: SyncMode) -> None:
    with requests_mock.Mocker() as http:
        mock_activity(http, 1788220800, 1788307199, [])
        mock_activity(http, 1788307200, 1788393599, [])
        mock_activity(http, 1788393600, 1788436800, [])

        output = read_activity(mode=mode)

    assert not output.errors
    assert not output.records
    assert len(http.request_history) == 3


@pytest.mark.parametrize("timestamp", ["2026-09-02T09:30:00.000000Z", "2026-09-02T09:30:00Z", "1788341400"])
def test_activity_cursor_accepts_api_and_legacy_timestamps(timestamp: str) -> None:
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG)
    stream = source.streams(CONFIG)[0]
    assert isinstance(stream, DeclarativeStream)
    assert isinstance(stream.retriever, SimpleRetriever)
    cursor = stream.retriever.cursor
    assert isinstance(cursor, DatetimeBasedCursor)

    assert cursor.parse_date(timestamp) == datetime(2026, 9, 2, 9, 30, tzinfo=timezone.utc)


@freeze_time("2026-09-03T12:00:00Z")
def test_activity_emits_iso_records_and_resumes_from_emitted_state() -> None:
    newest = {"id": "newest", "created_at": "2026-09-03T09:30:00.123456Z"}
    with requests_mock.Mocker() as http:
        mock_activity(http, 1788220800, 1788307199, [{"id": "first", "created_at": "2026-09-01T09:30:00.000000Z"}])
        mock_activity(http, 1788307200, 1788393599, [{"id": "second", "created_at": "2026-09-02T09:30:00Z"}])
        mock_activity(http, 1788393600, 1788436800, [newest, {"id": "older", "created_at": "2026-09-03T08:30:00.000000Z"}])

        first_sync = read_activity()

    assert not first_sync.errors
    assert {message.record.data["id"] for message in first_sync.records if message.record} == {"first", "second", "newest", "older"}
    assert len(http.request_history) == 3
    latest_state = first_sync.state_messages[-1].state
    assert latest_state is not None
    state = [latest_state]

    with freeze_time("2026-09-04T12:00:00Z"), requests_mock.Mocker() as http:
        mock_activity(http, 1788427800, 1788514199, [newest])
        mock_activity(http, 1788514200, 1788523200, [{"id": "next-sync", "created_at": "2026-09-04T10:00:00.000000Z"}])

        second_sync = read_activity(state)

    assert not second_sync.errors
    assert {message.record.data["id"] for message in second_sync.records if message.record} == {"newest", "next-sync"}
    assert len(http.request_history) == 2


@pytest.mark.parametrize("saved_cursor", ["1788341400", "2026-09-02T09:30:00.000000Z"])
@freeze_time("2026-09-03T12:00:00Z")
def test_activity_resumes_from_existing_stream_state(saved_cursor: str) -> None:
    state = StateBuilder().with_stream_state("activity", {"created_at": saved_cursor}).build()
    with requests_mock.Mocker() as http:
        mock_activity(http, 1788341400, 1788427799, [{"id": "second", "created_at": "2026-09-02T10:00:00.000000Z"}])
        mock_activity(http, 1788427800, 1788436800, [{"id": "third", "created_at": "2026-09-03T10:00:00.000000Z"}])

        output = read_activity(state)

    assert not output.errors
    assert {message.record.data["id"] for message in output.records if message.record} == {"second", "third"}
    assert len(http.request_history) == 2
