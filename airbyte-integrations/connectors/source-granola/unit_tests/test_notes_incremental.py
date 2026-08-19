# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `notes` incremental slice bounds on `source-granola`.

The Granola API treats `created_before=<date>` as excluding that whole day, so
day-truncated slice bounds dropped every record created on a slice boundary day.
These tests assert the exact `created_after` / `created_before` pairs sent for a
range spanning several 30-day slices, and that boundary-day records are emitted.
"""

from pathlib import Path

import pytest
import requests_mock
from freezegun import freeze_time

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
_NOW = "2026-01-15T12:00:00Z"
_CONFIG = {"api_key": "test-key", "start_date": "2025-10-12"}
_NOTES_URL = "https://public-api.granola.ai/v1/notes"

# Boundary days under the previous day-truncated bounds: with start_date 2025-10-12
# and step P30D, slices ended on 2025-11-10, 2025-12-10 and 2026-01-09.
_BOUNDARY_NOTES = [
    {"id": "note-boundary-1", "created_at": "2025-11-10T15:00:00Z"},
    {"id": "note-boundary-2", "created_at": "2025-12-10T08:30:00Z"},
    {"id": "note-boundary-3", "created_at": "2026-01-09T23:59:59Z"},
]
_MID_SLICE_NOTE = {"id": "note-mid-slice", "created_at": "2025-10-20T10:00:00Z"}

_EXPECTED_SLICE_BOUNDS = [
    ("2025-10-12T00:00:00Z", "2025-11-10T23:59:59Z"),
    ("2025-11-11T00:00:00Z", "2025-12-10T23:59:59Z"),
    ("2025-12-11T00:00:00Z", "2026-01-09T23:59:59Z"),
    ("2026-01-10T00:00:00Z", _NOW),
]


def _read_notes(state=None):
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream("notes", SyncMode.incremental).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=_CONFIG, state=state)
    return read(source, _CONFIG, catalog, state)


def _requested_slice_bounds(mocker):
    return {
        (request.qs["created_after"][0], request.qs["created_before"][0])
        for request in mocker.request_history
        if "created_after" in request.qs
    }


def _note_for(request):
    """Return the notes whose cursor falls inside the requested slice bounds."""
    after = request.qs["created_after"][0].upper()
    before = request.qs["created_before"][0].upper()
    return [note for note in _BOUNDARY_NOTES + [_MID_SLICE_NOTE] if after <= note["created_at"] <= before]


def _slice_response(request, context):
    return {"notes": _note_for(request), "hasMore": False}


@freeze_time(_NOW)
def test_slice_bounds_are_contiguous_second_granular_datetimes():
    with requests_mock.Mocker() as mocker:
        mocker.get(_NOTES_URL, json={"notes": [], "hasMore": False})
        _read_notes()
        requested = _requested_slice_bounds(mocker)

    expected = {(after.lower(), before.lower()) for after, before in _EXPECTED_SLICE_BOUNDS}
    assert requested == expected


@freeze_time(_NOW)
def test_boundary_day_records_are_emitted():
    with requests_mock.Mocker() as mocker:
        mocker.get(_NOTES_URL, json=_slice_response)
        output = _read_notes()

    emitted = {message.record.data["id"] for message in output.records}
    assert emitted == {note["id"] for note in _BOUNDARY_NOTES} | {_MID_SLICE_NOTE["id"]}


@freeze_time(_NOW)
@pytest.mark.parametrize("state_value", ["2025-12-20", "2025-12-20T00:00:00Z"])
def test_date_only_and_datetime_state_both_resume(state_value):
    state = StateBuilder().with_stream_state("notes", {"created_at": state_value}).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_NOTES_URL, json=_slice_response)
        output = _read_notes(state)
        requested = _requested_slice_bounds(mocker)

    assert output.errors == []
    assert min(after for after, _ in requested) == "2025-12-20t00:00:00z"
