# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Regression test for stuck-cursor bug (oncall #12930).

The `notes` stream uses day-precision datetime_format ("%Y-%m-%d") for slice
boundaries. If cursor_granularity is finer (e.g. PT0.000001S), the slice end
computed as `next_start - granularity` loses sub-day precision when formatted,
creating gaps that prevent merge_intervals from merging consecutive slices.
The cursor then stays pinned near the start date. With P1D granularity the
intervals merge correctly and the cursor advances.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture
def manifest():
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def _get_incremental_sync(manifest: dict, stream_name: str) -> dict:
    """Extract the incremental_sync config for a given stream definition."""
    streams = manifest["definitions"]["streams"]
    stream = streams[stream_name]
    return stream["incremental_sync"]


def test_notes_cursor_granularity_matches_datetime_format(manifest):
    """cursor_granularity must match the precision of datetime_format.

    datetime_format="%Y-%m-%d" has day precision, so cursor_granularity must be P1D.
    If it were finer (e.g. PT0.000001S), slice boundaries would lose sub-day
    precision after formatting, preventing interval merging.
    """
    incremental_sync = _get_incremental_sync(manifest, "notes")

    assert incremental_sync["datetime_format"] == "%Y-%m-%d"
    assert incremental_sync["cursor_granularity"] == "P1D", (
        f"cursor_granularity must be P1D for day-precision datetime_format, "
        f"got {incremental_sync['cursor_granularity']}"
    )


def test_notes_slice_boundaries_merge_with_p1d_granularity(manifest):
    """Verify consecutive slice boundaries have no gaps with P1D granularity.

    With step=P1M and cursor_granularity=P1D, the end of one slice should be
    exactly one day before the start of the next slice (i.e. start + step - P1D).
    When formatted with "%Y-%m-%d", increment(end) == next_start, enabling
    merge_intervals to merge them.
    """
    incremental_sync = _get_incremental_sync(manifest, "notes")
    datetime_format = incremental_sync["datetime_format"]
    granularity = incremental_sync["cursor_granularity"]

    assert granularity == "P1D"

    # Simulate two consecutive slice boundaries
    slice_start = datetime(2024, 1, 1)
    # With step=P1M, next slice starts ~Feb 1
    next_slice_start = datetime(2024, 2, 1)

    # slice_end = next_slice_start - granularity (P1D = 1 day)
    slice_end = next_slice_start - timedelta(days=1)

    # Format with the connector's datetime_format
    formatted_end = slice_end.strftime(datetime_format)
    assert formatted_end == "2024-01-31"

    # Verify that increment(formatted_end, P1D) == next_slice_start formatted
    # i.e., "2024-01-31" + 1 day == "2024-02-01"
    parsed_end = datetime.strptime(formatted_end, datetime_format)
    incremented = parsed_end + timedelta(days=1)
    formatted_next = next_slice_start.strftime(datetime_format)

    assert incremented.strftime(datetime_format) == formatted_next, (
        f"Increment of slice end ({formatted_end} + P1D = {incremented.strftime(datetime_format)}) "
        f"must equal next slice start ({formatted_next}) for intervals to merge"
    )


@pytest.mark.parametrize(
    "granularity,should_merge",
    [
        pytest.param("P1D", True, id="day_granularity_merges"),
        pytest.param("PT0.000001S", False, id="microsecond_granularity_creates_gaps"),
    ],
)
def test_granularity_format_alignment(granularity, should_merge):
    """Demonstrate that only P1D granularity produces mergeable intervals with day format.

    With day-precision formatting, sub-day granularities create gaps because
    the formatted end loses precision below the day level.
    """
    datetime_format = "%Y-%m-%d"
    slice_start = datetime(2024, 3, 1)
    next_slice_start = datetime(2024, 4, 1)

    if granularity == "P1D":
        delta = timedelta(days=1)
    elif granularity == "PT0.000001S":
        delta = timedelta(microseconds=1)
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")

    slice_end = next_slice_start - delta
    formatted_end = slice_end.strftime(datetime_format)

    # Check if increment(formatted_end) == next_slice_start
    parsed_end = datetime.strptime(formatted_end, datetime_format)
    incremented = parsed_end + delta
    formatted_next = next_slice_start.strftime(datetime_format)

    intervals_merge = incremented.strftime(datetime_format) == formatted_next
    assert intervals_merge == should_merge
