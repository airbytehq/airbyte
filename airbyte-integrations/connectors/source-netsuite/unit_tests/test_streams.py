#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from requests_oauthlib import OAuth1
from source_netsuite.constraints import (
    INCREMENTAL_CURSOR,
    MAX_NETSUITE_UTC_OFFSET_HOURS,
    NETSUITE_INPUT_DATE_FORMATS,
    NETSUITE_OUTPUT_DATETIME_FORMAT,
    SLICE_DATE_FORMAT,
)
from source_netsuite.errors import DateFormatExeption
from source_netsuite.streams import IncrementalNetsuiteStream

from airbyte_cdk.sources.streams.http import HttpStream


# Every whole-hour UTC offset a NetSuite account can be configured to, from Eniwetok to
# Kiritimati. The dead-zone guarantee has to hold across all of them.
NETSUITE_ACCOUNT_UTC_OFFSETS = list(range(-12, 15))

# Cursor values spanning the UTC day, including both sides of the point where backing off by
# MAX_NETSUITE_UTC_OFFSET_HOURS starts costing an extra day.
CURSORS_ACROSS_THE_DAY = [
    "2026-03-15T00:00:00Z",
    "2026-03-15T03:00:00Z",
    "2026-03-15T11:59:59Z",
    "2026-03-15T12:00:00Z",
    "2026-03-15T23:59:59Z",
]


def _make_stream(start_datetime: str = "2026-01-01T00:00:00Z", window_in_days: int = 1) -> IncrementalNetsuiteStream:
    auth = MagicMock(spec=OAuth1)
    return IncrementalNetsuiteStream(
        auth=auth,
        object_name="journalentry",
        base_url="https://1234.suitetalk.api.netsuite.com",
        start_datetime=start_datetime,
        window_in_days=window_in_days,
    )


def _queried_from_utc(slice_start: str, account_offset_hours: int) -> datetime:
    """
    Resolve a slice's start bound the way NetSuite does.

    A bare date in a `q` filter means midnight on that date *in the account's configured
    timezone*, so the instant the query actually opens at depends on the account.
    """
    account_tz = timezone(timedelta(hours=account_offset_hours))
    local_midnight = datetime.strptime(slice_start, SLICE_DATE_FORMAT).replace(tzinfo=account_tz)
    return local_midnight.astimezone(timezone.utc)


def _as_utc(cursor: str) -> datetime:
    return datetime.strptime(cursor, NETSUITE_OUTPUT_DATETIME_FORMAT).replace(tzinfo=timezone.utc)


@freeze_time("2026-03-16T10:00:00Z")
@pytest.mark.parametrize("account_offset_hours", NETSUITE_ACCOUNT_UTC_OFFSETS)
@pytest.mark.parametrize("cursor", CURSORS_ACROSS_THE_DAY)
def test_first_slice_opens_at_or_before_the_cursor_on_every_account_timezone(cursor, account_offset_hours):
    """
    The dead-zone guarantee: no record newer than the cursor may fall outside the query window.

    NetSuite resolves the slice's bare-date bound in the account's own timezone. If that
    resolved instant lands *after* the cursor, every record modified in between is skipped
    permanently. This must hold for any account timezone, not just UTC.
    """
    stream = _make_stream()

    slices = list(stream.stream_slices(stream_state={INCREMENTAL_CURSOR: cursor}))

    assert _queried_from_utc(slices[0]["start"], account_offset_hours) <= _as_utc(cursor)


@pytest.mark.parametrize("account_offset_hours", NETSUITE_ACCOUNT_UTC_OFFSETS)
def test_the_guarantee_above_would_fail_on_the_pre_fix_bound(account_offset_hours):
    """
    Proof that the test above has teeth.

    The pre-fix code truncated the cursor to its own date. On any account behind UTC that
    bound resolves to *after* the cursor, which is the reported defect. Asserting the failure
    here keeps the guarantee test from silently degrading into a tautology.
    """
    cursor = "2026-03-15T03:00:00Z"
    pre_fix_start = datetime.strptime(cursor, NETSUITE_OUTPUT_DATETIME_FORMAT).date().strftime(SLICE_DATE_FORMAT)

    resolved = _queried_from_utc(pre_fix_start, account_offset_hours)

    if account_offset_hours < -3:
        # e.g. US Pacific (-7): "03/15/2026" means 07:00Z, but the cursor is 03:00Z, so
        # anything modified in [03:00Z, 07:00Z) is never requested by any sync.
        assert resolved > _as_utc(cursor)
    else:
        assert resolved <= _as_utc(cursor)


@freeze_time("2026-03-16T10:00:00Z")
def test_reported_dead_zone_record_is_covered():
    """The reporter's exact scenario: PDT account, cursor 03:00Z, record modified at 04:15Z."""
    stream = _make_stream()
    slices = list(stream.stream_slices(stream_state={INCREMENTAL_CURSOR: "2026-03-15T03:00:00Z"}))

    opens_at = _queried_from_utc(slices[0]["start"], account_offset_hours=-7)
    dead_zone_record = datetime(2026, 3, 15, 4, 15, tzinfo=timezone.utc)

    assert opens_at <= dead_zone_record


@freeze_time("2026-03-16T10:00:00Z")
@pytest.mark.parametrize(
    "cursor,expected_first_start",
    [
        # Backing off 12h only costs an extra day when the cursor sits early in the UTC day.
        pytest.param("2026-03-15T00:00:00Z", "2026-03-14", id="midnight_cursor_reaches_back_one_day"),
        pytest.param("2026-03-15T03:00:00Z", "2026-03-14", id="early_cursor_reaches_back_one_day"),
        pytest.param("2026-03-15T11:59:59Z", "2026-03-14", id="just_before_noon_reaches_back_one_day"),
        pytest.param("2026-03-15T12:00:00Z", "2026-03-15", id="noon_cursor_costs_nothing"),
        pytest.param("2026-03-15T23:59:59Z", "2026-03-15", id="late_cursor_costs_nothing"),
    ],
)
def test_lookback_is_at_most_one_day_and_often_free(cursor, expected_first_start):
    """
    Cost control. Re-reading is bounded to a single extra day, and is skipped entirely when the
    cursor is late enough in the UTC day that no account timezone can overshoot it. This matters
    because `parse_response` issues one sub-request per listed record before state filtering.
    """
    stream = _make_stream()

    slices = list(stream.stream_slices(stream_state={INCREMENTAL_CURSOR: cursor}))

    assert slices[0]["start"] == expected_first_start


@freeze_time("2026-03-16T10:00:00Z")
def test_slices_are_contiguous_and_do_not_overlap():
    """
    Overlapping slices would double-fetch and emit duplicates, since the state filter only
    drops records older than the cursor, not records already seen in a previous slice.
    """
    stream = _make_stream(window_in_days=3)

    slices = list(stream.stream_slices(stream_state={INCREMENTAL_CURSOR: "2026-03-10T12:30:00Z"}))

    assert slices[0]["start"] == "2026-03-10"
    for earlier, later in zip(slices, slices[1:]):
        assert earlier["end"] == later["start"]
    for window in slices:
        span = datetime.strptime(window["end"], SLICE_DATE_FORMAT) - datetime.strptime(window["start"], SLICE_DATE_FORMAT)
        assert span == timedelta(days=3)


@freeze_time("2026-03-16T10:00:00Z")
def test_slices_cover_through_today():
    stream = _make_stream()

    slices = list(stream.stream_slices(stream_state={INCREMENTAL_CURSOR: "2026-03-15T03:00:00Z"}))

    assert slices[-1]["end"] == "2026-03-17"


@freeze_time("2026-03-16T10:00:00Z")
def test_future_state_returns_no_slices():
    stream = _make_stream()

    assert list(stream.stream_slices(stream_state={INCREMENTAL_CURSOR: "2026-04-01T00:00:00Z"})) == []


@freeze_time("2026-03-16T10:00:00Z")
def test_configured_start_datetime_is_used_without_state():
    stream = _make_stream(start_datetime="2026-03-15T00:00:00Z")

    slices = list(stream.stream_slices(stream_state=None))

    assert slices[0]["start"] == "2026-03-14"


@pytest.mark.parametrize("format_index", range(len(NETSUITE_INPUT_DATE_FORMATS)))
def test_request_params_renders_bounds_in_the_accounts_date_format(format_index):
    """
    Slice bounds are stored timezone-neutrally and rendered at request time, so whichever
    format the account accepts is the one that reaches the `q` parameter.
    """
    stream = _make_stream()
    stream.index_datetime_format = format_index
    expected_format = NETSUITE_INPUT_DATE_FORMATS[format_index]

    params = stream.request_params(stream_slice={"start": "2026-03-14", "end": "2026-03-15"})

    expected_start = datetime(2026, 3, 14).strftime(expected_format)
    expected_end = datetime(2026, 3, 15).strftime(expected_format)
    assert params["q"] == f'{INCREMENTAL_CURSOR} AFTER "{expected_start}" AND {INCREMENTAL_CURSOR} BEFORE "{expected_end}"'


@pytest.mark.parametrize("format_index", range(len(NETSUITE_INPUT_DATE_FORMATS)))
def test_request_params_never_emits_a_datetime_literal(format_index):
    """
    NetSuite's N/query layer rejects datetime literals in `q`, replying `Parse of date/time
    "..." failed with date format "M/d/yy" in time zone <account tz>`. Guard against a
    datetime format being reintroduced into the query.
    """
    stream = _make_stream()
    stream.index_datetime_format = format_index

    query = stream.request_params(stream_slice={"start": "2026-03-14", "end": "2026-03-15"})["q"]

    assert "T00:00:00Z" not in query
    assert ":" not in query


@pytest.mark.parametrize("date_format", NETSUITE_INPUT_DATE_FORMATS)
def test_candidate_formats_carry_no_time_component(date_format):
    assert not any(directive in date_format for directive in ("%H", "%M", "%S", "%f", "%z", "T", "Z"))


def test_max_offset_covers_every_netsuite_timezone():
    assert MAX_NETSUITE_UTC_OFFSET_HOURS >= -min(NETSUITE_ACCOUNT_UTC_OFFSETS)


def test_rejected_date_format_re_reads_the_same_slice():
    """
    A rejected date format must not cost a slice.

    `should_retry` advances the format index and raises `DateFormatExeption`. Previously that
    exception was swallowed and the slice yielded nothing, with nothing to ever re-read it --
    silently losing every record in that window. The slice must be re-issued instead.
    """
    stream = _make_stream()
    stream_slice = {"start": "2026-03-14", "end": "2026-03-15"}
    record = {INCREMENTAL_CURSOR: "2026-03-15T04:15:00Z"}
    attempted_slices = []
    attempted_formats = []

    def fake_parent_read(*args, **kwargs):
        attempted_slices.append(kwargs["stream_slice"])
        attempted_formats.append(stream.default_datetime_format)
        if len(attempted_slices) == 1:
            # what should_retry does before raising
            stream.index_datetime_format += 1
            raise DateFormatExeption
        return iter([record])

    with patch.object(HttpStream, "read_records", side_effect=fake_parent_read):
        emitted = list(stream.read_records(stream_slice=stream_slice))

    assert emitted == [record], "the record in the rejected slice must still be emitted"
    assert attempted_slices == [stream_slice, stream_slice], "the same slice must be retried"
    assert attempted_formats == [NETSUITE_INPUT_DATE_FORMATS[0], NETSUITE_INPUT_DATE_FORMATS[1]]


def test_slice_is_skipped_only_once_every_format_is_exhausted():
    """The retry loop must terminate rather than spin when no format is accepted."""
    stream = _make_stream()
    stream_slice = {"start": "2026-03-14", "end": "2026-03-15"}
    attempts = []

    def always_rejected(*args, **kwargs):
        attempts.append(kwargs["stream_slice"])
        stream.index_datetime_format += 1
        raise DateFormatExeption

    with patch.object(HttpStream, "read_records", side_effect=always_rejected):
        emitted = list(stream.read_records(stream_slice=stream_slice))

    assert emitted == []
    assert len(attempts) == len(NETSUITE_INPUT_DATE_FORMATS)
