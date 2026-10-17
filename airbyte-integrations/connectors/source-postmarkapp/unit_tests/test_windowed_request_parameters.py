# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


_EASTERN = ZoneInfo("America/New_York")
_WALL_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
_SLICE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
_PARAMETERS = yaml.safe_load(_YAML_FILE_PATH.read_text())["definitions"]["windowed_request_parameters"]
_JINJA = JinjaInterpolation()


def _render(key, start, end):
    stream_slice = {"start_time": start.strftime(_SLICE_FORMAT), "end_time": end.strftime(_SLICE_FORMAT)}
    return _JINJA.eval(_PARAMETERS[key], config={}, stream_slice=stream_slice)


def _readings(wall_time):
    """The UTC instants Postmark may read an Eastern wall time as: two during the repeated November hour, one otherwise."""
    naive = datetime.strptime(wall_time, _WALL_TIME_FORMAT)
    return {naive.replace(tzinfo=_EASTERN, fold=fold).astimezone(timezone.utc) for fold in (0, 1)}


def _is_repeated(wall_time):
    return len(_readings(wall_time)) > 1


@pytest.mark.parametrize("year", range(2024, 2032))
def test_filters_match_eastern_time_and_cover_the_window_under_either_reading(year):
    instant = datetime(year, 1, 1, tzinfo=timezone.utc)
    while instant.year == year:
        # Windows start on the hour or, after an incremental resume, at any second.
        for start in (instant, instant + timedelta(minutes=17, seconds=23)):
            end = start + timedelta(minutes=29, seconds=59)
            fromdate, todate = _render("fromdate", start, end), _render("todate", start, end)
            exact_fromdate = start.astimezone(_EASTERN).strftime(_WALL_TIME_FORMAT)
            exact_todate = (end + timedelta(seconds=1)).astimezone(_EASTERN).strftime(_WALL_TIME_FORMAT)

            assert max(_readings(fromdate)) <= start, (start, fromdate)
            assert min(_readings(todate)) >= end + timedelta(seconds=1), (end, todate)
            if not _is_repeated(exact_fromdate):
                assert fromdate == exact_fromdate, (start, fromdate)
            if not _is_repeated(exact_todate):
                assert todate == exact_todate, (end, todate)
        instant += timedelta(hours=1)


@pytest.mark.parametrize(
    "start, end, expected_fromdate, expected_todate",
    [
        # 05:00-06:00Z (EDT) and 06:00-07:00Z (EST) are both 01:00-02:00 Eastern on 2025-11-02.
        ("2025-11-02T04:30:00+0000", "2025-11-02T04:59:59+0000", "2025-11-02T00:30:00", "2025-11-02T01:00:00"),
        ("2025-11-02T05:30:00+0000", "2025-11-02T05:30:00+0000", "2025-11-02T00:59:59", "2025-11-02T01:30:01"),
        ("2025-11-02T06:30:00+0000", "2025-11-02T06:30:00+0000", "2025-11-02T01:30:00", "2025-11-02T02:00:00"),
        ("2025-11-02T07:00:00+0000", "2025-11-02T07:29:59+0000", "2025-11-02T02:00:00", "2025-11-02T02:30:00"),
    ],
)
def test_requests_in_the_repeated_hour_stay_within_it(start, end, expected_fromdate, expected_todate):
    start, end = datetime.strptime(start, _SLICE_FORMAT), datetime.strptime(end, _SLICE_FORMAT)

    assert _render("fromdate", start, end) == expected_fromdate
    assert _render("todate", start, end) == expected_todate
