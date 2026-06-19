# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Regression test for oncall #12932 / #12926.

source-lever-hiring uses epoch-millisecond datetime_format ("%ms") with
DatetimeBasedCursor. If cursor_granularity is finer than 1ms (e.g. PT0.000001S),
serialized slice boundaries lose sub-millisecond precision, creating gaps that
prevent merge_intervals from merging consecutive slices. The per-partition cursor
then stays pinned near the start date, re-reading entire history every sync.

Fix: cursor_granularity must be PT0.001S (1 millisecond) to match the format
resolution.
"""

from pathlib import Path

import pytest
import yaml
from isodate import parse_duration


def _collect_cursors(node, path=""):
    """Recursively collect all DatetimeBasedCursor nodes from the manifest."""
    results = []
    if isinstance(node, dict):
        if node.get("type") == "DatetimeBasedCursor":
            results.append((path, node))
        for key, value in node.items():
            results.extend(_collect_cursors(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            results.extend(_collect_cursors(item, f"{path}[{i}]"))
    return results


@pytest.fixture(scope="module")
def manifest():
    manifest_file = Path(__file__).parent.parent / "manifest.yaml"
    with open(manifest_file) as f:
        return yaml.safe_load(f)


def test_all_epoch_ms_cursors_have_millisecond_granularity(manifest):
    """Every DatetimeBasedCursor using epoch-ms format must have PT0.001S granularity."""
    cursors = _collect_cursors(manifest)
    assert len(cursors) > 0, "Expected to find DatetimeBasedCursor nodes in manifest"

    epoch_ms_cursors = [
        (path, cursor)
        for path, cursor in cursors
        if cursor.get("datetime_format") == "%ms"
    ]
    assert len(epoch_ms_cursors) > 0, "Expected to find cursors with %ms format"

    for path, cursor in epoch_ms_cursors:
        granularity = cursor.get("cursor_granularity")
        assert granularity is not None, (
            f"DatetimeBasedCursor at {path} missing cursor_granularity"
        )
        duration = parse_duration(granularity)
        total_seconds = duration.total_seconds()
        assert total_seconds == 0.001, (
            f"DatetimeBasedCursor at {path} has cursor_granularity={granularity} "
            f"({total_seconds}s) but should be PT0.001S (0.001s) to match "
            f"epoch-millisecond datetime_format"
        )


@pytest.mark.parametrize(
    "granularity_iso,should_merge",
    [
        pytest.param("PT0.001S", True, id="millisecond_granularity_merges"),
        pytest.param("PT0.000001S", False, id="microsecond_granularity_does_not_merge"),
    ],
)
def test_interval_merge_with_epoch_ms_format(granularity_iso, should_merge):
    """Simulate the merge_intervals logic with epoch-ms formatted slice boundaries.

    When cursor_granularity is PT0.000001S (microseconds) and datetime_format is
    "%ms", the slice end is computed as next_start - 0.000001, but formatting to
    milliseconds truncates it, leaving a gap > granularity between intervals so
    they never merge. With PT0.001S, the gap equals exactly the granularity and
    intervals merge correctly.
    """
    from datetime import timedelta

    granularity = parse_duration(granularity_iso)
    granularity_td = timedelta(seconds=granularity.total_seconds())

    # Simulate two adjacent 30-day windows starting at epoch ms = 1660694400000
    window1_start_ms = 1660694400000  # 2022-08-17T00:00:00Z in ms
    window2_start_ms = window1_start_ms + 30 * 24 * 3600 * 1000  # +30 days

    # The CDK computes slice end as: next_window_start - cursor_granularity
    # Then formats it using datetime_format ("%ms" → integer milliseconds)
    window1_end_exact = window2_start_ms - granularity_td.total_seconds() * 1000

    # Simulate formatting to epoch-ms (integer truncation)
    window1_end_formatted = int(window1_end_exact)

    # For intervals to merge: increment(end) >= next_start
    # increment adds cursor_granularity to the end value
    incremented_end = window1_end_formatted + granularity_td.total_seconds() * 1000

    intervals_merge = incremented_end >= window2_start_ms

    assert intervals_merge == should_merge, (
        f"With granularity={granularity_iso}: "
        f"window1_end_exact={window1_end_exact}, "
        f"window1_end_formatted={window1_end_formatted}, "
        f"incremented_end={incremented_end}, "
        f"window2_start={window2_start_ms}, "
        f"merge={intervals_merge} (expected {should_merge})"
    )
