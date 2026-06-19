# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Regression test for oncall #12930: notes stream cursor never advances.

The ``notes`` stream uses day-precision ``datetime_format`` (``%Y-%m-%d``) but
previously declared ``cursor_granularity: PT0.000001S`` (microseconds). The CDK
computes slice boundaries as ``next_start - cursor_granularity``, and when
formatted with day precision the sub-day info is truncated, preventing interval
merging and pinning the cursor near the start date.

With the fix (``cursor_granularity: P1D``), intervals merge correctly and the
per-partition cursor advances past the saved value.
"""

from urllib.parse import parse_qs, urlparse

from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.productboard.com"


def read_from_stream(cfg, stream: str, sync_mode, state=None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(cfg, state), cfg, catalog, state)


@freeze_time("2022-11-16 12:00:00+00:00")
def test_notes_cursor_advances_across_windows(requests_mock):
    """The per-partition cursor must advance past the saved value after an incremental read.

    With the bug (PT0.000001S granularity + day-precision format), the cursor stays
    pinned at the start. With the fix (P1D granularity), intervals merge and the
    cursor advances to reflect the most recent record seen.
    """
    # Mock the notes endpoint: return one record per window with updatedAt = updatedFrom date
    def _notes_response(request, context):
        qs = parse_qs(urlparse(request.url).query)
        updated_from = qs.get("updatedFrom", ["2022-01-01"])[0]
        context.status_code = 200
        return {
            "data": [
                {
                    "id": f"note-{updated_from}",
                    "title": "Test note",
                    "updatedAt": f"{updated_from}T10:00:00.000000Z",
                }
            ],
            "pageCursor": None,
        }

    requests_mock.get(f"{BASE}/notes", json=_notes_response)

    # Saved state: cursor a few months back -> several monthly windows are generated
    saved_cursor = "2022-08-16T00:00:00.000000Z"
    state = (
        StateBuilder()
        .with_stream_state(
            "notes",
            {"updatedAt": saved_cursor},
        )
        .build()
    )

    output = read_from_stream(TEST_CONFIG, "notes", SyncMode.incremental, state)

    # The cursor must advance past the saved value
    final_state = output.most_recent_state.stream_state.__dict__
    final_cursor = final_state.get("updatedAt", "")

    # The saved cursor is day-level comparable: strip time portion for comparison
    saved_cursor_date = saved_cursor[:10]  # "2022-08-16"
    assert final_cursor > saved_cursor_date, (
        f"Cursor did not advance past saved value. "
        f"Saved: {saved_cursor_date}, Final: {final_cursor}. "
        f"This indicates the cursor_granularity/datetime_format mismatch bug is present."
    )


@freeze_time("2022-11-16 12:00:00+00:00")
def test_notes_cursor_does_not_stay_stuck_at_start(requests_mock):
    """Even starting from the very beginning, cursor must advance to the latest record."""
    def _notes_response(request, context):
        qs = parse_qs(urlparse(request.url).query)
        updated_from = qs.get("updatedFrom", ["2022-01-01"])[0]
        context.status_code = 200
        return {
            "data": [
                {
                    "id": f"note-{updated_from}",
                    "title": "Test note",
                    "updatedAt": f"{updated_from}T12:00:00.000000Z",
                }
            ],
            "pageCursor": None,
        }

    requests_mock.get(f"{BASE}/notes", json=_notes_response)

    output = read_from_stream(TEST_CONFIG, "notes", SyncMode.incremental)

    # With no prior state, cursor should advance past the config start_date
    final_state = output.most_recent_state.stream_state.__dict__
    final_cursor = final_state.get("updatedAt", "")
    config_start_date = "2022-01-01"  # day-precision comparison

    assert final_cursor > config_start_date, (
        f"Cursor stayed stuck at/near start date. "
        f"Start: {config_start_date}, Final: {final_cursor}. "
        f"Cursor should have advanced to reflect recent records."
    )
