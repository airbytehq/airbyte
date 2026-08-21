# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-nasa manifest.yaml.

Validates that cursor_granularity is aligned with datetime_format precision.
Regression test for oncall#12929: PT0.000001S granularity with day-precision
format causes merge_intervals to fail, pinning the cursor near start_date.
"""

import pathlib

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


GRANULARITY_BY_FORMAT = {
    "%Y-%m-%d": "P1D",
    "%Y-%m-%dT%H:%M:%SZ": "PT1S",
    "%Y-%m-%dT%H:%M:%S%z": "PT1S",
    "%Y-%m-%d %H:%M:%SZ": "PT1S",
}


def _collect_incremental_syncs(manifest):
    """Collect all incremental_sync blocks from both definitions and streams."""
    syncs = []
    defs = manifest.get("definitions", {}).get("streams", {})
    for name, stream in defs.items():
        inc = stream.get("incremental_sync")
        if inc:
            syncs.append((f"definitions.streams.{name}", inc))
    for i, stream in enumerate(manifest.get("streams", [])):
        inc = stream.get("incremental_sync")
        if inc:
            syncs.append((f"streams[{i}].{stream.get('name', i)}", inc))
    return syncs


def test_cursor_granularity_matches_datetime_format(manifest):
    """cursor_granularity must match the precision of datetime_format.

    If datetime_format is day-precision (%Y-%m-%d), granularity must be P1D.
    A finer granularity (e.g. PT0.000001S) causes slice boundaries to be
    truncated when serialized, preventing merge_intervals from coalescing
    consecutive intervals. This pins the cursor and re-reads all history.
    """
    syncs = _collect_incremental_syncs(manifest)
    assert syncs, "Expected at least one incremental_sync block in the manifest"

    for location, inc in syncs:
        fmt = inc.get("datetime_format")
        granularity = inc.get("cursor_granularity")
        expected = GRANULARITY_BY_FORMAT.get(fmt)
        if expected:
            assert (
                granularity == expected
            ), f"{location}: cursor_granularity={granularity!r} does not match datetime_format={fmt!r} (expected {expected!r})"


def test_cursor_granularity_is_not_microseconds(manifest):
    """Regression: cursor_granularity must never be PT0.000001S with day-precision format."""
    syncs = _collect_incremental_syncs(manifest)
    for location, inc in syncs:
        granularity = inc.get("cursor_granularity", "")
        assert (
            granularity != "PT0.000001S"
        ), f"{location}: cursor_granularity is PT0.000001S (microseconds) which is incompatible with day-precision datetime_format"


def test_both_manifest_locations_are_consistent(manifest):
    """The definitions block and streams block must have identical incremental_sync settings."""
    syncs = _collect_incremental_syncs(manifest)
    granularities = [(loc, inc.get("cursor_granularity")) for loc, inc in syncs]
    values = {g for _, g in granularities}
    assert len(values) == 1, f"Inconsistent cursor_granularity across manifest locations: {granularities}"
