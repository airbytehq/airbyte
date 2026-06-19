# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Regression test for oncall #12929: cursor_granularity must match datetime_format precision.

When cursor_granularity (PT0.000001S) is finer than datetime_format (%Y-%m-%d = day precision),
the CDK's concurrent cursor merge_intervals fails because serialized slice boundaries lose
sub-day precision. This causes intervals to never merge and the cursor stays pinned near start_date.

Fix: set cursor_granularity to P1D for day-precision streams.
"""

from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


def read_from_stream(cfg, stream: str, sync_mode, state=None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(cfg, state), cfg, catalog, state)


@freeze_time("2022-04-15")
def test_apod_cursor_advances_across_windows(requests_mock):
    """Verify that the nasa_apod cursor advances past the saved state across multiple monthly windows.

    With cursor_granularity=P1D and datetime_format=%Y-%m-%d, consecutive daily slices
    merge correctly and the persisted cursor advances to the most recent record date.
    """

    # Each monthly window returns one record dated at its start_date parameter.
    def _apod_response(request, context):
        qs = parse_qs(urlparse(request.url).query)
        start_date = qs.get("start_date", ["2022-01-01"])[0]
        context.status_code = 200
        return [
            {
                "date": start_date,
                "title": f"APOD for {start_date}",
                "explanation": "Test",
                "url": "https://example.com/image.jpg",
                "media_type": "image",
                "service_version": "v1",
            }
        ]

    requests_mock.get("https://api.nasa.gov/planetary/apod", json=_apod_response)

    # Saved state a few months back -> several monthly windows should be generated.
    saved_cursor = "2022-01-15"
    state = (
        StateBuilder()
        .with_stream_state(
            "nasa_apod",
            {"date": saved_cursor},
        )
        .build()
    )

    output = read_from_stream(TEST_CONFIG, "nasa_apod", SyncMode.incremental, state)

    # The cursor must advance past the saved value.
    final_state = output.most_recent_state
    assert final_state is not None, "No state message emitted"
    cursor_value = final_state.stream_state.__dict__["date"]

    assert cursor_value > saved_cursor, (
        f"Cursor did not advance: stayed at {cursor_value!r} (saved was {saved_cursor!r}). "
        "This indicates cursor_granularity is still mismatched with datetime_format."
    )


@freeze_time("2022-04-15")
def test_apod_incremental_emits_records(requests_mock):
    """Verify that incremental reads emit records for each monthly window."""

    def _apod_response(request, context):
        qs = parse_qs(urlparse(request.url).query)
        start_date = qs.get("start_date", ["2022-01-01"])[0]
        context.status_code = 200
        return [
            {
                "date": start_date,
                "title": f"APOD for {start_date}",
                "explanation": "Test",
                "url": "https://example.com/image.jpg",
                "media_type": "image",
                "service_version": "v1",
            }
        ]

    requests_mock.get("https://api.nasa.gov/planetary/apod", json=_apod_response)

    saved_cursor = "2022-01-15"
    state = (
        StateBuilder()
        .with_stream_state(
            "nasa_apod",
            {"date": saved_cursor},
        )
        .build()
    )

    output = read_from_stream(TEST_CONFIG, "nasa_apod", SyncMode.incremental, state)

    # Should emit records from multiple monthly windows between saved cursor and "today" (2022-04-15)
    assert len(output.records) > 0, "No records emitted during incremental read"
