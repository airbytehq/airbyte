# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import datetime
from datetime import timedelta, timezone

import pytest

from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    CustomFormatConcurrentStreamStateConverter,
)


EPOCH_FORMAT = "%s"


def _make_converter(cursor_granularity: timedelta) -> CustomFormatConcurrentStreamStateConverter:
    return CustomFormatConcurrentStreamStateConverter(
        datetime_format=EPOCH_FORMAT,
        input_datetime_formats=[EPOCH_FORMAT],
        cursor_granularity=cursor_granularity,
    )


@pytest.mark.parametrize(
    "granularity, should_merge",
    [
        pytest.param(timedelta(seconds=1), True, id="PT1S-intervals-merge"),
        pytest.param(timedelta(microseconds=1), False, id="PT0.000001S-intervals-stay-fragmented"),
    ],
)
def test_cursor_granularity_interval_merging(granularity: timedelta, should_merge: bool) -> None:
    """Regression for oncall #12931: cursor_granularity finer than datetime_format.

    When `cursor_granularity` is `PT0.000001S` (microseconds) but
    `datetime_format` is `%s` (epoch seconds), the CDK computes each slice end
    as `next_start - 1us`. Formatting that with `%s` truncates the microseconds,
    creating a ~1s gap between consecutive slices. `merge_intervals` requires
    `increment(end) >= next_start`, but `end + 1us` after truncation is still
    ~1s short, so the intervals never merge and the cursor stays pinned.

    With `PT1S`, `end = next_start - 1s` survives formatting, and
    `end + 1s == next_start`, so the intervals merge correctly.
    """
    converter = _make_converter(granularity)

    # Monthly window boundaries (Jan-Jun 2024)
    boundary_dts = [
        datetime.datetime(2024, m, 1, tzinfo=timezone.utc)
        for m in range(1, 7)
    ]

    # Build intervals replicating the CDK's slice-end computation:
    #   end_dt = next_start - granularity
    #   formatted_end = output_format(end_dt)  -> truncates to integer seconds
    #   round-tripped_end = parse_timestamp(formatted_end)
    # The round-trip through output_format is what causes the truncation.
    intervals = []
    for i in range(len(boundary_dts) - 1):
        start_dt = boundary_dts[i]
        end_dt = boundary_dts[i + 1] - granularity

        # Round-trip through the converter's format (epoch seconds) to replicate
        # the serialization truncation that happens in the CDK.
        formatted_end = converter.output_format(end_dt)
        round_tripped_end = converter.parse_timestamp(formatted_end)

        intervals.append({"start": start_dt, "end": round_tripped_end})

    merged = converter.merge_intervals(intervals)

    if should_merge:
        assert len(merged) == 1, (
            f"Expected all {len(intervals)} intervals to merge into 1, "
            f"got {len(merged)}"
        )
    else:
        assert len(merged) == len(intervals), (
            f"Expected intervals to stay fragmented ({len(intervals)}), "
            f"but got {len(merged)} after merging"
        )
