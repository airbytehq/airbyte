#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests
from freezegun import freeze_time
from requests_oauthlib import OAuth1
from source_netsuite.constraints import (
    INCREMENTAL_CURSOR,
    NETSUITE_INPUT_DATE_FORMATS,
    NETSUITE_OUTPUT_DATETIME_FORMAT,
    SLICE_DATE_FORMAT,
)
from source_netsuite.errors import DateFormatExeption
from source_netsuite.streams import IncrementalNetsuiteStream, NetsuiteStream

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http import HttpStream


def _make_incremental_stream(start_datetime: str = "2026-01-01T00:00:00Z", window_in_days: int = 1) -> IncrementalNetsuiteStream:
    return IncrementalNetsuiteStream(
        auth=MagicMock(spec=OAuth1),
        object_name="journalentry",
        base_url="https://test.suitetalk.api.netsuite.com",
        start_datetime=start_datetime,
        window_in_days=window_in_days,
    )


def _make_base_stream(object_name: str = "journalentry") -> NetsuiteStream:
    stream = NetsuiteStream.__new__(NetsuiteStream)
    stream.object_name = object_name
    stream.base_url = "https://test.suitetalk.api.netsuite.com"
    stream.start_datetime = "2024-01-01T00:00:00Z"
    stream.window_in_days = 30
    stream.schemas = {}
    stream._records_attempted = 0
    stream._user_error_skipped = 0
    stream.index_datetime_format = 0
    stream.raise_on_http_errors = True
    stream._session = MagicMock()
    return stream


def _make_response(status_code: int, json_data: dict) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.json.return_value = json_data
    return response


USER_ERROR_JSON = {
    "o:errorDetails": [
        {
            "o:errorCode": "USER_ERROR",
            "detail": "This record has been locked by a user defined workflow.",
        }
    ]
}


def _queried_from_utc(slice_start: str, account_offset_hours: int) -> datetime:
    account_tz = timezone(timedelta(hours=account_offset_hours))
    local_midnight = datetime.strptime(slice_start, SLICE_DATE_FORMAT).replace(tzinfo=account_tz)
    return local_midnight.astimezone(timezone.utc)


def _as_utc(cursor: str) -> datetime:
    return datetime.strptime(cursor, NETSUITE_OUTPUT_DATETIME_FORMAT).replace(tzinfo=timezone.utc)


@freeze_time("2026-03-16T10:00:00Z")
@pytest.mark.parametrize("account_offset_hours", range(-12, 15))
@pytest.mark.parametrize(
    "cursor",
    [
        "2026-03-15T00:00:00Z",
        "2026-03-15T03:00:00Z",
        "2026-03-15T11:59:59Z",
        "2026-03-15T12:00:00Z",
        "2026-03-15T23:59:59Z",
    ],
)
def test_first_slice_opens_at_or_before_cursor_in_every_account_timezone(cursor, account_offset_hours):
    slices = list(_make_incremental_stream().stream_slices(stream_state={INCREMENTAL_CURSOR: cursor}))

    assert _queried_from_utc(slices[0]["start"], account_offset_hours) <= _as_utc(cursor)


@freeze_time("2026-03-16T10:00:00Z")
@pytest.mark.parametrize(
    "cursor, expected_start",
    [
        ("2026-03-15T03:00:00Z", "2026-03-14"),
        ("2026-03-15T11:59:59Z", "2026-03-14"),
        ("2026-03-15T12:00:00Z", "2026-03-15"),
        ("2026-03-15T23:59:59Z", "2026-03-15"),
    ],
)
def test_cursor_lookback_is_bounded_to_one_day(cursor, expected_start):
    slices = list(_make_incremental_stream().stream_slices(stream_state={INCREMENTAL_CURSOR: cursor}))

    assert slices[0]["start"] == expected_start


@pytest.mark.parametrize("format_index", range(len(NETSUITE_INPUT_DATE_FORMATS)))
def test_request_params_renders_slice_in_account_date_format(format_index):
    stream = _make_incremental_stream()
    stream.index_datetime_format = format_index
    expected_format = NETSUITE_INPUT_DATE_FORMATS[format_index]

    params = stream.request_params(stream_slice={"start": "2026-03-14", "end": "2026-03-15"})

    expected_start = datetime(2026, 3, 14).strftime(expected_format)
    expected_end = datetime(2026, 3, 15).strftime(expected_format)
    assert params["q"] == f'{INCREMENTAL_CURSOR} AFTER "{expected_start}" AND {INCREMENTAL_CURSOR} BEFORE "{expected_end}"'
    assert ":" not in params["q"]


def test_rejected_date_format_retries_same_slice():
    stream = _make_incremental_stream()
    stream_slice = {"start": "2026-03-14", "end": "2026-03-15"}
    record = {INCREMENTAL_CURSOR: "2026-03-15T04:15:00Z"}
    attempts = []

    def fake_parent_read(*args, **kwargs):
        attempts.append((kwargs["stream_slice"], stream.default_datetime_format))
        if len(attempts) == 1:
            stream.index_datetime_format += 1
            raise DateFormatExeption
        return iter([record])

    with patch.object(HttpStream, "read_records", side_effect=fake_parent_read):
        emitted = list(stream.read_records(stream_slice=stream_slice))

    assert emitted == [record]
    assert [attempt[0] for attempt in attempts] == [stream_slice, stream_slice]
    assert [attempt[1] for attempt in attempts] == NETSUITE_INPUT_DATE_FORMATS[:2]


def test_fetch_record_tracks_workflow_locked_record():
    stream = _make_base_stream()
    stream._send_request = MagicMock(return_value=_make_response(400, USER_ERROR_JSON))

    records = list(stream.fetch_record({"links": [{"href": "https://test/record/99"}]}, {}))

    assert records == []
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 1


@pytest.mark.parametrize(
    "json_body",
    [
        {},
        {"o:errorDetails": []},
        {"o:errorDetails": [{"o:errorCode": "INVALID_PARAMETER"}]},
    ],
)
def test_non_user_errors_are_not_counted_as_workflow_locks(json_body):
    stream = _make_base_stream()

    stream._track_skipped_record(_make_response(400, json_body))

    assert stream._user_error_skipped == 0


def test_malformed_error_response_is_ignored():
    stream = _make_base_stream()
    response = MagicMock(spec=requests.Response)
    response.json.side_effect = ValueError("invalid JSON")

    stream._track_skipped_record(response)

    assert stream._user_error_skipped == 0


def test_skipped_records_emit_actionable_warning(caplog):
    stream = _make_base_stream("salesorder")
    stream._records_attempted = 10
    stream._user_error_skipped = 3

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        stream._emit_skipped_records_summary()

    assert "salesorder" in caplog.records[-1].message
    assert "3 of 10" in caplog.records[-1].message
    assert "workflow" in caplog.records[-1].message.lower()


@pytest.mark.parametrize(
    "attempted, skipped, should_fail",
    [
        (100, 10, False),
        (100, 50, False),
        (100, 51, True),
        (10, 10, True),
    ],
)
def test_sync_fails_only_when_more_than_half_of_records_are_locked(attempted, skipped, should_fail):
    stream = _make_base_stream()
    stream._records_attempted = attempted
    stream._user_error_skipped = skipped

    if should_fail:
        with pytest.raises(AirbyteTracedException) as exc_info:
            stream._emit_skipped_records_summary()
        assert exc_info.value.failure_type == FailureType.system_error
    else:
        stream._emit_skipped_records_summary()
