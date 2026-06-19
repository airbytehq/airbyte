# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Regression test for oncall #12931 / #12926: cursor_granularity must match datetime_format precision.

When cursor_granularity (PT0.000001S) is finer than the epoch-second datetime_format ("%s"),
serialized slice boundaries lose sub-second precision. This creates gaps that prevent
merge_intervals from merging consecutive slices, so the per-partition cursor stays pinned
near the start date.

Fix: set cursor_granularity to PT1S for all DatetimeBasedCursor blocks using "%s".
"""

import datetime
from pathlib import Path

import isodate
import pytest
import yaml

from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    CustomFormatConcurrentStreamStateConverter,
)


def _load_manifest(manifest_path: Path) -> dict:
    with open(manifest_path) as f:
        return yaml.safe_load(f)


def _collect_incremental_cursors(manifest: dict) -> list[dict]:
    """Collect all incremental_sync blocks from the manifest (both definitions and top-level streams)."""
    cursors = []
    # Top-level streams
    for stream in manifest.get("streams", []):
        if "incremental_sync" in stream:
            cursors.append(stream["incremental_sync"])
    # Definition streams
    for stream in manifest.get("definitions", {}).get("streams", {}).values():
        if isinstance(stream, dict) and "incremental_sync" in stream:
            cursors.append(stream["incremental_sync"])
    return cursors


def test_all_epoch_cursors_use_pt1s_granularity(manifest_path: Path) -> None:
    """Every DatetimeBasedCursor with epoch-second format must have PT1S granularity."""
    manifest = _load_manifest(manifest_path)
    cursors = _collect_incremental_cursors(manifest)
    assert cursors, "Expected at least one incremental_sync block in the manifest"

    for cursor in cursors:
        fmt = cursor.get("datetime_format", "")
        granularity = cursor.get("cursor_granularity", "")
        if fmt == "%s":
            assert granularity == "PT1S", f"cursor_granularity must be PT1S for epoch-second format, got {granularity}"


@pytest.mark.parametrize(
    "granularity_iso,expect_recovery",
    [
        pytest.param("PT0.000001S", False, id="microsecond_granularity_broken"),
        pytest.param("PT1S", True, id="second_granularity_correct"),
    ],
)
def test_epoch_second_interval_recovery(granularity_iso: str, expect_recovery: bool) -> None:
    """Verify that slice boundaries survive epoch-second serialization round-trip.

    With PT1S granularity, `parse(format(boundary - granularity)) + granularity` recovers
    the original boundary exactly. With sub-second granularity it does not, which breaks
    the CDK's merge_intervals logic and causes the cursor to get stuck.
    """
    fmt = "%s"
    granularity = isodate.parse_duration(granularity_iso)
    converter = CustomFormatConcurrentStreamStateConverter(
        datetime_format=fmt,
        input_datetime_formats=[fmt],
    )

    boundary = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end = boundary - granularity

    # Round-trip through the format
    formatted = converter.output_format(end)
    parsed = converter.parse_timestamp(formatted)
    recovered = parsed + granularity

    if expect_recovery:
        assert recovered == boundary, f"Expected boundary recovery: {recovered} != {boundary}"
    else:
        assert recovered != boundary, f"Expected broken recovery but got exact match (test premise invalid)"
