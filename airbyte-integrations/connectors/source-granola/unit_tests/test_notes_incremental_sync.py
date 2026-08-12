from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_API_URL = "https://public-api.granola.ai/v1/notes"
_CONFIG = {"api_key": "test-api-key", "start_date": "2026-01-01"}


def get_source(config: dict, state=None) -> YamlDeclarativeSource:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return YamlDeclarativeSource(
        path_to_yaml=str(manifest_path),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state,
    )


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _notes_response(request, notes):
    query = parse_qs(urlparse(request.url).query)
    created_after = _parse_timestamp(query["created_after"][0])
    created_before_value = query.get("created_before", [None])[0]
    created_before = (
        _parse_timestamp(created_before_value)
        if created_before_value and "T" in created_before_value
        else datetime.strptime(created_before_value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if created_before_value
        else None
    )
    filtered_notes = [
        note
        for note in notes
        if _parse_timestamp(note["created_at"]) >= created_after
        and (created_before is None or _parse_timestamp(note["created_at"]) < created_before)
    ]
    return {"notes": filtered_notes, "cursor": "", "hasMore": False}


def _read_notes(notes, config=_CONFIG, state=None):
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream("notes", SyncMode.incremental).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_API_URL, json=lambda request, context: _notes_response(request, notes))
        output = read(source, config=config, catalog=catalog, state=state)
        requests = list(mocker.request_history)
    return output, requests


def test_boundary_date_note_is_not_dropped():
    notes = [
        {"id": "before-boundary", "created_at": "2026-01-29T23:59:59Z"},
        {"id": "on-boundary", "created_at": "2026-01-30T00:00:00.123Z"},
        {"id": "after-boundary", "created_at": "2026-01-31T00:00:00Z"},
    ]

    output, _ = _read_notes(notes)

    assert [record.record.data["id"] for record in output.records] == [
        "before-boundary",
        "on-boundary",
        "after-boundary",
    ]


def test_notes_request_is_unbounded():
    notes = [{"id": "note-1", "created_at": "2026-01-02T00:00:00Z"}]

    output, requests = _read_notes(notes)

    assert len(output.records) == 1
    assert len(requests) == 1
    query = parse_qs(urlparse(requests[0].url).query)
    assert query["created_after"] == ["2026-01-01T00:00:00Z"]
    assert "created_before" not in query


def test_legacy_date_state_is_accepted_and_emits_iso_state():
    notes = [{"id": "note-2", "created_at": "2026-06-02T12:34:56.123Z"}]
    state = StateBuilder().with_stream_state("notes", {"created_at": "2026-06-01"}).build()
    config = {"api_key": "test-api-key", "start_date": "2026-01-01"}

    output, requests = _read_notes(notes, config=config, state=state)

    query = parse_qs(urlparse(requests[0].url).query)
    assert query["created_after"] == ["2026-06-01T00:00:00Z"]
    assert len(output.records) == 1
    latest_state = output.state_messages[-1].state.stream.stream_state
    assert latest_state.created_at == "2026-06-02T12:34:56Z"
