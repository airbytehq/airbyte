#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from requests_oauthlib import OAuth1
from source_netsuite.constraints import INCREMENTAL_CURSOR, NETSUITE_OUTPUT_DATETIME_FORMAT
from source_netsuite.streams import IncrementalNetsuiteStream


def _make_stream(start_datetime: str = "2026-01-01T00:00:00Z", window_in_days: int = 1) -> IncrementalNetsuiteStream:
    auth = MagicMock(spec=OAuth1)
    return IncrementalNetsuiteStream(
        auth=auth,
        object_name="journalentry",
        base_url="https://1234.suitetalk.api.netsuite.com",
        start_datetime=start_datetime,
        window_in_days=window_in_days,
    )


@freeze_time("2026-03-16T10:00:00Z")
@pytest.mark.parametrize(
    "state_cursor,expected_start,expected_end",
    [
        pytest.param(
            "2026-03-15T03:00:00Z",
            "2026-03-15T00:00:00Z",
            "2026-03-16T00:00:00Z",
            id="cursor_mid_day_zeroes_time_to_midnight_utc",
        ),
        pytest.param(
            "2026-03-15T00:00:00Z",
            "2026-03-15T00:00:00Z",
            "2026-03-16T00:00:00Z",
            id="cursor_at_midnight_stays_at_midnight",
        ),
        pytest.param(
            "2026-03-15T23:59:59Z",
            "2026-03-15T00:00:00Z",
            "2026-03-16T00:00:00Z",
            id="cursor_near_end_of_day_zeroes_to_midnight",
        ),
    ],
)
def test_stream_slices_uses_datetime_format(state_cursor, expected_start, expected_end):
    """stream_slices must produce explicit UTC datetime bounds, not date-only strings."""
    stream = _make_stream(window_in_days=1)
    state = {INCREMENTAL_CURSOR: state_cursor}

    slices = list(stream.stream_slices(stream_state=state))

    first_slice = slices[0]
    assert first_slice["start"] == expected_start
    assert first_slice["end"] == expected_end


@freeze_time("2026-03-16T10:00:00Z")
def test_stream_slices_no_dead_zone():
    """Records between sync time and account-local midnight must not be skipped.

    Before the fix, a cursor at 03:00Z on March 15 would produce a slice
    starting at "03/15/2026", which NetSuite (PDT) interprets as 07:00Z.
    A record at 04:15Z would fall in the dead zone [03:00Z, 07:00Z).
    After the fix, the slice starts at "2026-03-15T00:00:00Z" (UTC midnight),
    which is unambiguous and covers all records from midnight UTC onward.
    """
    stream = _make_stream(window_in_days=1)
    state = {INCREMENTAL_CURSOR: "2026-03-15T03:00:00Z"}

    slices = list(stream.stream_slices(stream_state=state))

    first_start = slices[0]["start"]
    # The start bound must be an explicit UTC datetime at midnight, not a date-only string
    parsed = datetime.strptime(first_start, NETSUITE_OUTPUT_DATETIME_FORMAT)
    assert parsed.hour == 0 and parsed.minute == 0 and parsed.second == 0
    # A record at 04:15Z on 2026-03-15 is AFTER the slice start (00:00Z), so it is included
    record_time = datetime(2026, 3, 15, 4, 15, 0)
    assert record_time >= parsed


@freeze_time("2026-03-16T10:00:00Z")
def test_stream_slices_future_state_returns_empty():
    """A state cursor in the future should return no slices."""
    stream = _make_stream(window_in_days=1)
    state = {INCREMENTAL_CURSOR: "2026-04-01T00:00:00Z"}

    slices = list(stream.stream_slices(stream_state=state))

    assert slices == []


@freeze_time("2026-03-16T10:00:00Z")
def test_stream_slices_multi_day_window():
    """Multi-day windows should produce datetime-formatted bounds with correct intervals."""
    stream = _make_stream(window_in_days=3)
    state = {INCREMENTAL_CURSOR: "2026-03-10T12:30:00Z"}

    slices = list(stream.stream_slices(stream_state=state))

    # First slice: March 10 00:00:00Z -> March 13 00:00:00Z
    assert slices[0]["start"] == "2026-03-10T00:00:00Z"
    assert slices[0]["end"] == "2026-03-13T00:00:00Z"
    # Second slice: March 13 00:00:00Z -> March 16 00:00:00Z
    assert slices[1]["start"] == "2026-03-13T00:00:00Z"
    assert slices[1]["end"] == "2026-03-16T00:00:00Z"


@freeze_time("2026-03-16T10:00:00Z")
def test_stream_slices_default_start_datetime():
    """When no stream state is provided, slices use the configured start_datetime."""
    stream = _make_stream(start_datetime="2026-03-15T00:00:00Z", window_in_days=1)

    slices = list(stream.stream_slices(stream_state=None))

    assert slices[0]["start"] == "2026-03-15T00:00:00Z"
    assert slices[0]["end"] == "2026-03-16T00:00:00Z"


@freeze_time("2026-03-16T10:00:00Z")
def test_request_params_uses_datetime_in_query():
    """request_params must embed datetime-formatted bounds in the q parameter."""
    stream = _make_stream(window_in_days=1)
    stream_slice = {"start": "2026-03-15T00:00:00Z", "end": "2026-03-16T00:00:00Z"}

    params = stream.request_params(stream_slice=stream_slice)

    expected_q = f'{INCREMENTAL_CURSOR} AFTER "2026-03-15T00:00:00Z" AND {INCREMENTAL_CURSOR} BEFORE "2026-03-16T00:00:00Z"'
    assert params["q"] == expected_q


def test_date_format_fallback_ordering():
    """The datetime format should be first in the list so fallback works for accounts that reject it."""
    from source_netsuite.constraints import NETSUITE_INPUT_DATE_FORMATS

    assert NETSUITE_INPUT_DATE_FORMATS[0] == "%Y-%m-%dT%H:%M:%SZ"
    # Date-only formats should still be present for fallback
    assert "%m/%d/%Y" in NETSUITE_INPUT_DATE_FORMATS
    assert "%Y-%m-%d" in NETSUITE_INPUT_DATE_FORMATS
