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
    MAX_NETSUITE_UTC_OFFSET_HOURS,
    NETSUITE_INPUT_DATE_FORMATS,
    NETSUITE_OUTPUT_DATETIME_FORMAT,
    RECORD_PATH,
    SCHEMA_HEADERS,
    SLICE_DATE_FORMAT,
)
from source_netsuite.errors import DateFormatExeption
from source_netsuite.streams import IncrementalNetsuiteStream, NetsuiteStream

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import FailureType, SyncMode
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


def _make_base_stream(object_name: str = "journalentry") -> NetsuiteStream:
    """Build a minimal `NetsuiteStream` instance for testing."""
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
    stream._schema_session = MagicMock()
    stream._http_client = MagicMock()
    return stream


def _make_response(status_code: int, json_data: dict) -> MagicMock:
    """Build a mock `requests.Response`."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


_USER_ERROR_JSON = {
    "o:errorDetails": [
        {
            "o:errorCode": "USER_ERROR",
            "detail": "Error while accessing a resource. This record has been locked by a user defined workflow.",
        }
    ]
}


# ---------------------------------------------------------------------------
# _track_skipped_record
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "json_body, expected_skipped",
    [
        pytest.param(
            _USER_ERROR_JSON,
            1,
            id="user_error_increments_counter",
        ),
        pytest.param(
            {"o:errorDetails": [{"o:errorCode": "INVALID_PARAMETER", "detail": "some issue"}]},
            0,
            id="other_error_code_no_increment",
        ),
        pytest.param(
            {"o:errorDetails": []},
            0,
            id="empty_error_details_no_increment",
        ),
        pytest.param(
            {},
            0,
            id="missing_error_details_no_increment",
        ),
    ],
)
def test_track_skipped_record(json_body, expected_skipped):
    stream = _make_base_stream()
    response = _make_response(400, json_body)

    stream._track_skipped_record(response)

    assert stream._user_error_skipped == expected_skipped


def test_track_skipped_record_malformed_json():
    stream = _make_base_stream()
    response = MagicMock(spec=requests.Response)
    response.status_code = 400
    response.json.side_effect = ValueError("No JSON")

    stream._track_skipped_record(response)

    assert stream._user_error_skipped == 0


# ---------------------------------------------------------------------------
# fetch_record
# ---------------------------------------------------------------------------


def test_fetch_record_yields_on_200():
    stream = _make_base_stream()
    ok_resp = _make_response(200, {"id": "42", "type": "journalentry"})
    stream._http_client.send_request.return_value = (MagicMock(), ok_resp)
    url = "https://test/record/42"

    results = list(stream.fetch_record({"links": [{"href": url}]}, {}))

    assert len(results) == 1
    assert results[0]["id"] == "42"
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 0
    stream._http_client.send_request.assert_called_once_with(
        http_method="GET",
        url=url,
        request_kwargs={},
        params={"expandSubResources": True},
    )


def test_fetch_record_skips_and_tracks_user_error():
    stream = _make_base_stream()
    err_resp = _make_response(400, _USER_ERROR_JSON)
    stream._http_client.send_request.return_value = (MagicMock(), err_resp)
    url = "https://test/record/99"

    results = list(stream.fetch_record({"links": [{"href": url}]}, {}))

    assert results == []
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 1
    stream._http_client.send_request.assert_called_once_with(
        http_method="GET",
        url=url,
        request_kwargs={},
        params={"expandSubResources": True},
    )


def test_fetch_record_does_not_track_non_400():
    stream = _make_base_stream()
    resp_500 = _make_response(500, {})
    stream._http_client.send_request.return_value = (MagicMock(), resp_500)
    url = "https://test/record/1"

    results = list(stream.fetch_record({"links": [{"href": url}]}, {}))

    assert results == []
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 0
    stream._http_client.send_request.assert_called_once_with(
        http_method="GET",
        url=url,
        request_kwargs={},
        params={"expandSubResources": True},
    )


# ---------------------------------------------------------------------------
# _emit_skipped_records_summary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attempted, skipped, should_raise",
    [
        pytest.param(100, 0, False, id="no_skips_no_warning"),
        pytest.param(100, 10, False, id="10pct_skipped_warning_only"),
        pytest.param(200, 100, False, id="exactly_50pct_no_raise"),
        pytest.param(100, 51, True, id="51pct_raises_traced_exception"),
        pytest.param(200, 101, True, id="50.5pct_raises_traced_exception"),
        pytest.param(10, 10, True, id="100pct_raises_traced_exception"),
    ],
)
def test_emit_skipped_records_summary(attempted, skipped, should_raise):
    stream = _make_base_stream()
    stream._records_attempted = attempted
    stream._user_error_skipped = skipped

    if should_raise:
        with pytest.raises(AirbyteTracedException) as exc_info:
            stream._emit_skipped_records_summary()
        assert exc_info.value.failure_type == FailureType.system_error
        assert str(skipped) in exc_info.value.message
        assert "workflow locks" in exc_info.value.message
    else:
        stream._emit_skipped_records_summary()


def test_emit_skipped_records_summary_warning_content(caplog):
    stream = _make_base_stream("salesorder")
    stream._records_attempted = 10
    stream._user_error_skipped = 3

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        stream._emit_skipped_records_summary()

    assert len(caplog.records) >= 1
    warning_msg = caplog.records[-1].message
    assert "salesorder" in warning_msg
    assert "3 of 10" in warning_msg
    assert "workflow" in warning_msg.lower()


# ---------------------------------------------------------------------------
# should_retry — typo fix verification
# ---------------------------------------------------------------------------


def test_should_retry_user_error_corrected_spelling(caplog):
    stream = _make_base_stream()
    response = _make_response(400, _USER_ERROR_JSON)

    with caplog.at_level(logging.ERROR, logger="airbyte"):
        result = stream.should_retry(response)

    assert result is False
    error_msgs = [r.message for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(error_msgs) >= 1
    assert "occurred" in error_msgs[0]
    assert "occured" not in error_msgs[0]


@pytest.mark.parametrize(
    "status_code, json_data, expected",
    [
        (429, {}, True),
        (500, {}, True),
        (503, {}, True),
        (404, {}, False),
        (401, {}, False),
        (400, {"o:errorDetails": [{"o:errorCode": "SOME_OTHER"}]}, False),
        (403, {"o:errorDetails": "unexpected"}, False),
    ],
)
def test_should_retry_default_fallback(status_code, json_data, expected):
    stream = _make_base_stream()

    assert stream.should_retry(_make_response(status_code, json_data)) is expected


# ---------------------------------------------------------------------------
# Integration: mixed OK and USER_ERROR across multiple records
# ---------------------------------------------------------------------------


def test_fetch_record_accumulation_mixed_responses():
    stream = _make_base_stream()
    ok_resp = _make_response(200, {"id": "1", "type": "journalentry"})
    err_resp = _make_response(400, _USER_ERROR_JSON)
    call_count = 0

    def mock_send_request(**kwargs):
        nonlocal call_count
        call_count += 1
        return MagicMock(), ok_resp if call_count % 2 == 1 else err_resp

    stream._http_client.send_request.side_effect = mock_send_request

    all_results = []
    for i in range(6):
        all_results.extend(stream.fetch_record({"links": [{"href": f"https://test/record/{i}"}]}, {}))

    assert stream._records_attempted == 6
    assert stream._user_error_skipped == 3
    assert len(all_results) == 3


def _make_real_stream(stream_class=NetsuiteStream):
    return stream_class(
        auth=None,
        object_name="journalentry",
        base_url="https://1234.suitetalk.api.netsuite.com",
        start_datetime="2026-01-01T00:00:00Z",
        window_in_days=30,
    )


def _record_url(record_id):
    return f"https://1234.suitetalk.api.netsuite.com{RECORD_PATH}journalentry/{record_id}"


def test_full_refresh_reads_successful_record_and_skips_one_user_error(requests_mock):
    stream = _make_real_stream()
    collection_url = f"{stream.url_base}{RECORD_PATH}journalentry"
    requests_mock.get(
        collection_url,
        json={
            "items": [
                {"links": [{"href": _record_url(1)}]},
                {"links": [{"href": _record_url(2)}]},
            ],
            "hasMore": False,
        },
    )
    requests_mock.get(_record_url(1), json={"id": "1", "type": "journalentry"})
    requests_mock.get(_record_url(2), status_code=400, json=_USER_ERROR_JSON)

    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=None))

    assert records == [{"id": "1", "type": "journalentry"}]
    assert stream._records_attempted == 2
    assert stream._user_error_skipped == 1
    record_requests = [request for request in requests_mock.request_history if request.url.startswith(_record_url(""))]
    assert [request.qs["expandsubresources"] for request in record_requests] == [["true"], ["true"]]


def test_full_refresh_fails_when_all_records_have_user_errors(requests_mock):
    stream = _make_real_stream()
    collection_url = f"{stream.url_base}{RECORD_PATH}journalentry"
    requests_mock.get(
        collection_url,
        json={
            "items": [
                {"links": [{"href": _record_url(1)}]},
                {"links": [{"href": _record_url(2)}]},
            ],
            "hasMore": False,
        },
    )
    requests_mock.get(_record_url(1), status_code=400, json=_USER_ERROR_JSON)
    requests_mock.get(_record_url(2), status_code=400, json=_USER_ERROR_JSON)

    with pytest.raises(AirbyteTracedException) as exc_info:
        list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=None))

    assert exc_info.value.failure_type == FailureType.system_error
    assert stream._records_attempted == 2
    assert stream._user_error_skipped == 2


def test_incremental_retries_rejected_date_format_on_same_slice(requests_mock):
    stream = _make_real_stream(IncrementalNetsuiteStream)
    collection_url = f"{stream.url_base}{RECORD_PATH}journalentry"
    date_error = {
        "o:errorDetails": [
            {
                "o:errorCode": "INVALID_PARAMETER",
                "detail": 'Parse of date/time "03/14/2026" failed with date format "M/d/yy" in time zone America/Los_Angeles',
            }
        ]
    }
    requests_mock.get(
        collection_url,
        response_list=[
            {"status_code": 400, "json": date_error},
            {
                "status_code": 200,
                "json": {"items": [{"links": [{"href": _record_url(1)}]}], "hasMore": False},
            },
        ],
    )
    requests_mock.get(_record_url(1), json={"id": "1", "lastModifiedDate": "2026-03-15T04:15:00Z"})

    records = list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"start": "2026-03-14", "end": "2026-03-15"},
        )
    )

    expected_queries = [
        'lastmodifieddate after "03/14/2026" and lastmodifieddate before "03/15/2026"',
        'lastmodifieddate after "2026-03-14" and lastmodifieddate before "2026-03-15"',
    ]
    collection_requests = [
        request for request in requests_mock.request_history if request.path_url.startswith(f"{RECORD_PATH}journalentry?")
    ]
    assert records == [{"id": "1", "lastModifiedDate": "2026-03-15T04:15:00Z"}]
    assert [request.qs["q"][0] for request in collection_requests] == expected_queries


@pytest.mark.parametrize(
    "status_code, body, expected",
    [
        (404, None, {"title": "/missing-schema", "type": "string"}),
        (200, {"title": "journalentry", "type": "object"}, {"title": "journalentry", "type": "object"}),
    ],
)
def test_get_schema_uses_schema_headers(requests_mock, status_code, body, expected):
    stream = _make_real_stream()
    ref = "/missing-schema" if status_code == 404 else "/journalentry-schema"
    requests_mock.get(f"{stream.url_base}{ref}", status_code=status_code, json=body)

    assert stream.get_schema(ref) == expected
    assert requests_mock.last_request.headers["Accept"] == SCHEMA_HEADERS["Accept"]
