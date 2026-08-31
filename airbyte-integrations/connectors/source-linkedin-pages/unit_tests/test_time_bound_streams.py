# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Tests that the follower_statistics_time_bound and share_statistics_time_bound
streams produce midnight-aligned time intervals, satisfying LinkedIn's DAY
granularity constraint ("end − start ≥ 24 h").
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"
TIME_BOUND_STREAMS = ("follower_statistics_time_bound", "share_statistics_time_bound")


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _get_stream_config(manifest: dict, stream_name: str) -> dict:
    for stream in manifest["streams"]:
        if stream["name"] == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name!r} not found in manifest")


def _eval_jinja(expression: str, config: dict) -> str:
    interpolation = JinjaInterpolation()
    return interpolation.eval(expression, config=config, default=expression, parameters={})


@pytest.mark.parametrize("stream_name", TIME_BOUND_STREAMS, ids=TIME_BOUND_STREAMS)
def test_cursor_has_step_and_granularity(manifest, stream_name):
    """Each time_bound stream must define step and cursor_granularity."""
    cursor = _get_stream_config(manifest, stream_name)["incremental_sync"]
    assert cursor.get("step") == "P1D", "step must be P1D to match DAY granularity"
    assert cursor.get("cursor_granularity") == "P0D", "cursor_granularity must be P0D"


@pytest.mark.parametrize("stream_name", TIME_BOUND_STREAMS, ids=TIME_BOUND_STREAMS)
def test_end_datetime_is_midnight_aligned(manifest, stream_name):
    """end_datetime must resolve to T00:00:00Z (midnight UTC)."""
    cursor = _get_stream_config(manifest, stream_name)["incremental_sync"]
    end_dt_expr = cursor["end_datetime"]["datetime"]
    result = _eval_jinja(end_dt_expr, config={})
    assert result.endswith("T00:00:00Z"), f"end_datetime must be midnight-aligned, got {result}"
    parsed = datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")
    assert parsed.hour == 0 and parsed.minute == 0 and parsed.second == 0


@pytest.mark.parametrize("stream_name", TIME_BOUND_STREAMS, ids=TIME_BOUND_STREAMS)
def test_start_datetime_is_midnight_aligned_no_config(manifest, stream_name):
    """start_datetime without config['start_date'] must resolve to midnight UTC."""
    cursor = _get_stream_config(manifest, stream_name)["incremental_sync"]
    start_dt_expr = cursor["start_datetime"]["datetime"]
    result = _eval_jinja(start_dt_expr, config={})
    assert result.endswith("T00:00:00Z"), f"start_datetime must be midnight-aligned, got {result}"


@pytest.mark.parametrize("stream_name", TIME_BOUND_STREAMS, ids=TIME_BOUND_STREAMS)
def test_start_datetime_is_midnight_aligned_with_config(manifest, stream_name):
    """start_datetime with config['start_date'] must still resolve to midnight UTC."""
    cursor = _get_stream_config(manifest, stream_name)["incremental_sync"]
    start_dt_expr = cursor["start_datetime"]["datetime"]
    config = {"start_date": "2025-01-15T00:00:00Z"}
    result = _eval_jinja(start_dt_expr, config=config)
    assert result.endswith("T00:00:00Z"), f"start_datetime must be midnight-aligned, got {result}"


@pytest.mark.parametrize("stream_name", TIME_BOUND_STREAMS, ids=TIME_BOUND_STREAMS)
def test_end_minus_start_is_whole_days(manifest, stream_name):
    """The gap between start and end datetimes must be a whole number of days (≥ 0)."""
    cursor = _get_stream_config(manifest, stream_name)["incremental_sync"]
    start_result = _eval_jinja(cursor["start_datetime"]["datetime"], config={})
    end_result = _eval_jinja(cursor["end_datetime"]["datetime"], config={})
    start = datetime.strptime(start_result, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end_result, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    delta_seconds = (end - start).total_seconds()
    assert delta_seconds >= 0, "end_datetime must be >= start_datetime"
    assert delta_seconds % 86400 == 0, f"Gap must be a whole number of days, got {delta_seconds}s " f"({delta_seconds / 86400:.2f} days)"
