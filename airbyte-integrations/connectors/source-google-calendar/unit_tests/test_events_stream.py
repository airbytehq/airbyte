#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock-server tests for the `events` stream: updatedMin bounding, client-side filtering,
pagination and error handling.

Google rejects `updatedMin` bounds older than 29 days with a 410 (undocumented, measured),
so `events` is a `StateDelegatingStream` with `api_retention_period: P21D` for margin: with
no saved cursor, or one older than 21 days, the stale state is cleared and the full-refresh
stream re-reads the calendar (sending `updatedMin` only for a `start_date` within 21 days,
and dropping records older than `start_date` client-side); otherwise the incremental stream
sends `updatedMin` from the saved cursor and relies on the server-side filter. Cancelled
stubs, which carry no `updated`, are stamped with max(slice start, now - 1h) so they win
destination dedup. These tests pin the exact request parameters per case, the stub stamp,
and the failure classification of error responses.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.call_rate import HttpAPIBudget
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "client_id": "id",
    "client_secret": "secret",
    "client_refresh_token_2": "rt",
    "calendarid": "primary",
}

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_TOKEN_REQUEST = HttpRequest(
    _TOKEN_URL,
    body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt",
)
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "at", "expires_in": 3600}))
_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
_CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/primary"
_BASE_PARAMS = {"showDeleted": "true", "maxResults": "2500", "singleEvents": "false"}
_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _days_ago(n: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime(_DATETIME_FORMAT)


_RECORD = {"id": "e1", "updated": _days_ago(10)}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    # Backoff sleeps are skipped. The api_budget's own cool-down after a 429 would spin
    # without a real clock, so the 429 test disables budget updates explicitly.
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _events_request(updated_min: Optional[str] = None, page_token: Optional[str] = None) -> HttpRequest:
    params = dict(_BASE_PARAMS)
    if updated_min is not None:
        params["updatedMin"] = updated_min
    if page_token is not None:
        params["pageToken"] = page_token
    return HttpRequest(_EVENTS_URL, query_params=params)


def _items_response(*records, next_page_token: Optional[str] = None) -> HttpResponse:
    body: dict = {"items": list(records)}
    if next_page_token:
        body["nextPageToken"] = next_page_token
    return HttpResponse(json.dumps(body))


def _error_response(status_code: int, reason: Optional[str] = None, message: str = "error", body_code: Any = "status") -> HttpResponse:
    # body_code overrides the `code` field of the error body ("status" mirrors status_code, None omits it).
    error: dict = {"message": message}
    if body_code == "status":
        error["code"] = status_code
    elif body_code is not None:
        error["code"] = body_code
    if reason:
        error["errors"] = [{"reason": reason, "domain": "usageLimits"}]
    return HttpResponse(json.dumps({"error": error}), status_code=status_code)


def _catalog(sync_mode: SyncMode) -> Any:
    return CatalogBuilder().with_stream("events", sync_mode).build()


def _config(**overrides) -> Mapping[str, Any]:
    config = dict(_CONFIG)
    config.update(overrides)
    return config


def _mock_parent_partitions(http_mocker: HttpMocker) -> None:
    """Mock the partition parent: with `calendarid` set, only the configured calendar is read."""
    http_mocker.get(HttpRequest(_CALENDAR_URL), HttpResponse(json.dumps({"id": "primary"})))


def _read_events(http_mocker: HttpMocker, sync_mode: SyncMode, state=None, config=None, expecting_exception=False):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    _mock_parent_partitions(http_mocker)
    config = config or _config()
    source = get_source(config, state=state)
    return read(source, config, _catalog(sync_mode), state=state, expecting_exception=expecting_exception)


def _partition_state(cursor: str):
    """Stream state with one cursor for every calendar, under "state" where the
    StateDelegatingStream's retention check reads it."""
    return (
        StateBuilder().with_stream_state("events", {"use_global_cursor": True, "state": {"updated": cursor}, "lookback_window": 0}).build()
    )


def _stream_state(state_message) -> Mapping[str, Any]:
    return json.loads(json.dumps(state_message.state.stream.stream_state, default=lambda o: o.__dict__))


def _record_ids(output) -> list:
    return [message.record.data["id"] for message in output.records]


def _error_trace(output):
    assert output.errors, "expected the sync to emit an error trace message"
    return output.errors[0].trace.error


# --- request bounding -------------------------------------------------------------------


def test_full_refresh_no_state_sends_no_updated_min():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.full_refresh)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_no_state_no_start_date_sends_no_updated_min():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        assert _RECORD["updated"] in _stream_state(output.state_messages[-1])["state"]["updated"]
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_fresh_state_sends_updated_min():
    cursor = _days_ago(2)
    newer = {"id": "e2", "updated": _days_ago(1)}
    state = _partition_state(cursor)
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=cursor)
        http_mocker.get(request, _items_response(newer))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert _record_ids(output) == ["e2"]
        assert newer["updated"] in _stream_state(output.state_messages[-1])["state"]["updated"]
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_state_just_inside_retention_sends_updated_min():
    cursor = _days_ago(20)
    state = _partition_state(cursor)
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=cursor)
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert all(emitted != {} for emitted in map(_stream_state, output.state_messages))
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("age_days", [21.5, 22, 28], ids=["21.5d", "22d", "28d"])
def test_incremental_state_just_past_retention_drops_updated_min_and_resets_state(age_days):
    # Google's measured cut-off is 29 days; the connector keeps a week of margin at 21.
    state = _partition_state(_days_ago(age_days))
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        emitted_states = [_stream_state(message) for message in output.state_messages]
        assert emitted_states[0] == {}, "the stale cursor is cleared before the full re-read"
        assert _RECORD["updated"] in emitted_states[-1]["state"]["updated"]
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_stale_state_drops_updated_min_and_resets_state():
    state = _partition_state(_days_ago(60))
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        emitted_states = [_stream_state(message) for message in output.state_messages]
        assert emitted_states[0] == {}, "the stale cursor is cleared before the full re-read"
        assert _RECORD["updated"] in emitted_states[-1]["state"]["updated"]


def test_incremental_fresh_start_date_sends_updated_min():
    start_date = _days_ago(7)
    recent = {"id": "recent", "updated": _days_ago(3)}
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=start_date)
        http_mocker.get(request, _items_response(recent))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=start_date))

        assert output.errors == []
        assert _record_ids(output) == ["recent"]
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize(
    "age_days, sends_updated_min", [(20.5, True), (21.5, False), (28, False), (35, False)], ids=["20.5d", "21.5d", "28d", "35d"]
)
def test_start_date_guard_boundary(age_days, sends_updated_min):
    start_date = _days_ago(age_days)
    recent = {"id": "recent", "updated": _days_ago(1)}
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=start_date if sends_updated_min else None)
        http_mocker.get(request, _items_response(recent))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=start_date))

        assert output.errors == []
        assert _record_ids(output) == ["recent"]
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("age_days, sends_updated_min", [(7, True), (60, False)], ids=["recent", "old"])
def test_full_refresh_with_start_date_bounds_the_sync(age_days, sends_updated_min):
    start_date = _days_ago(age_days)
    older = {"id": "older", "updated": _days_ago(age_days + 30)}
    newer = {"id": "newer", "updated": _days_ago(1)}
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=start_date if sends_updated_min else None)
        http_mocker.get(request, _items_response(older, newer))

        output = _read_events(http_mocker, SyncMode.full_refresh, config=_config(start_date=start_date))

        assert output.errors == []
        assert _record_ids(output) == ["newer"]
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_stale_start_date_drops_updated_min():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=_days_ago(60)))

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 1)


# --- client-side filtering on the full-refresh branch -----------------------------------


def test_no_start_date_emits_old_events_and_unedited_recurring_series():
    old_series = {
        "id": "weekly_since_2023",
        "updated": _days_ago(3 * 365),
        "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"],
        "status": "confirmed",
    }
    old_one_off = {"id": "old", "updated": _days_ago(5 * 365)}
    cancelled = {"id": "gone", "status": "cancelled"}
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(), _items_response(old_series, old_one_off, _RECORD, cancelled))

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["weekly_since_2023", "old", "e1", "gone"]


def test_old_start_date_drops_records_modified_before_it_client_side():
    start_date = _days_ago(60)
    older = {"id": "older", "updated": _days_ago(90)}
    old_series = {"id": "series_edited_long_ago", "updated": _days_ago(365), "recurrence": ["RRULE:FREQ=WEEKLY"]}
    newer = {"id": "newer", "updated": _days_ago(30)}
    cancelled = {"id": "gone", "status": "cancelled"}
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(), _items_response(older, old_series, newer, cancelled))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=start_date))

        assert output.errors == []
        assert _record_ids(output) == ["newer", "gone"]


def test_seconds_precision_updated_is_parsed_and_kept():
    seconds_only = {"id": "s", "updated": (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(), _items_response(seconds_only))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=_days_ago(60)))

        assert output.errors == []
        assert _record_ids(output) == ["s"]
        assert seconds_only["updated"][:19] in _stream_state(output.state_messages[-1])["state"]["updated"]


def test_record_updated_slightly_in_the_future_is_kept():
    skewed = {"id": "skewed", "updated": (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime(_DATETIME_FORMAT)}
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(), _items_response(skewed))

        output = _read_events(http_mocker, SyncMode.full_refresh)

        assert output.errors == []
        assert _record_ids(output) == ["skewed"]


def test_incremental_branch_does_not_filter_client_side():
    cursor = _days_ago(2)
    state = _partition_state(cursor)
    server_filtered = {"id": "from_server", "updated": _days_ago(400)}
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(updated_min=cursor), _items_response(server_filtered))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert _record_ids(output) == ["from_server"]


# --- pagination and transformations -----------------------------------------------------


def test_pagination_follows_next_page_token_and_adds_calendar_id():
    first, second = {"id": "a", "updated": _days_ago(3)}, {"id": "b", "updated": _days_ago(2)}
    with HttpMocker() as http_mocker:
        page_1 = _events_request()
        page_2 = _events_request(page_token="t2")
        http_mocker.get(page_1, _items_response(first, next_page_token="t2"))
        http_mocker.get(page_2, _items_response(second))

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["a", "b"]
        assert {message.record.data["calendar_id"] for message in output.records} == {"primary"}
        assert second["updated"] in _stream_state(output.state_messages[-1])["state"]["updated"]
        http_mocker.assert_number_of_calls(page_1, 1)
        http_mocker.assert_number_of_calls(page_2, 1)


def _parse(value: str) -> datetime:
    return datetime.strptime(value, _DATETIME_FORMAT).replace(tzinfo=timezone.utc)


def test_cancelled_stub_is_stamped_with_a_cursor_that_out_dates_live_rows():
    cancelled = {"id": "x", "status": "cancelled"}
    record = {"id": "e1", "updated": _days_ago(1)}
    cursor = _days_ago(5)
    cursor_state = _partition_state(cursor)
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(updated_min=cursor), _items_response(cancelled, record))

        before = datetime.now(timezone.utc)
        output = _read_events(http_mocker, SyncMode.incremental, state=cursor_state)

        assert output.errors == []
        assert _record_ids(output) == ["x", "e1"]
        stub = output.records[0].record.data
        stamp = _parse(stub["updated"])
        assert timedelta(minutes=59) <= before - stamp <= timedelta(minutes=61), "stub is stamped one hour before the sync"
        assert stamp > _parse(record["updated"]) > _parse(cursor)
        assert _stream_state(output.state_messages[-1])["state"]["updated"] == stub["updated"], "the stamp becomes the cursor"


def test_cancelled_stub_only_sync_moves_the_cursor_past_the_input_state():
    cancelled = {"id": "gone", "status": "cancelled"}
    cursor = _days_ago(2)
    cursor_state = _partition_state(cursor)
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(updated_min=cursor), _items_response(cancelled))

        output = _read_events(http_mocker, SyncMode.incremental, state=cursor_state)

        assert output.errors == []
        stub = output.records[0].record.data
        assert _parse(stub["updated"]) > _parse(cursor)
        assert _stream_state(output.state_messages[-1])["state"]["updated"] == stub["updated"]


def test_cancelled_stub_with_a_fresh_cursor_takes_the_cursor_not_the_clock():
    cancelled = {"id": "gone", "status": "cancelled"}
    cursor = (datetime.now(timezone.utc) - timedelta(minutes=30)).strftime(_DATETIME_FORMAT)
    cursor_state = _partition_state(cursor)
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(updated_min=cursor), _items_response(cancelled))

        output = _read_events(http_mocker, SyncMode.incremental, state=cursor_state)

        assert output.errors == []
        assert output.records[0].record.data["updated"] == cursor
        assert _stream_state(output.state_messages[-1])["state"]["updated"] == cursor


# --- error handling ---------------------------------------------------------------------


def test_rate_limit_403_retries_then_succeeds():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, [_error_response(403, "userRateLimitExceeded"), _items_response(_RECORD)])

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 2)


@pytest.mark.parametrize("reason", [None, "rateLimitExceeded", "quotaExceeded"], ids=["no-reason", "rateLimitExceeded", "quotaExceeded"])
def test_429_retries_then_succeeds(monkeypatch, reason):
    monkeypatch.setattr(HttpAPIBudget, "update_from_response", lambda self, request, response: None)
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, [_error_response(429, reason), _items_response(_RECORD)])

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 2)


@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_server_error_retries_then_succeeds(status_code):
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, [_error_response(status_code), _items_response(_RECORD)])

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 2)


@pytest.mark.parametrize(
    "response, failure_type, message_fragments",
    [
        (
            _error_response(401, message="Invalid Credentials"),
            FailureType.config_error,
            ("rejected the OAuth credentials", "Re-authorize the connector"),
        ),
        (_error_response(403, message="Forbidden"), FailureType.config_error, ("lacks access to the configured calendar",)),
        (_error_response(403, "quotaExceeded"), FailureType.transient_error, ("quota for this project or user is exhausted",)),
        (_error_response(403, "dailyLimitExceeded"), FailureType.transient_error, ("quota for this project or user is exhausted",)),
        (
            _error_response(403, "quotaExceeded", body_code="403"),
            FailureType.transient_error,
            ("quota for this project or user is exhausted",),
        ),
        (
            _error_response(403, "quotaExceeded", body_code=None),
            FailureType.transient_error,
            ("quota for this project or user is exhausted",),
        ),
        (_error_response(404, message="Not Found"), FailureType.config_error, ('"Calendar Id" was not found', "or use 'primary'")),
    ],
    ids=["401", "403-plain", "403-quotaExceeded", "403-dailyLimitExceeded", "403-quota-string-code", "403-quota-no-code", "404"],
)
def test_non_retryable_errors_are_classified(response, failure_type, message_fragments):
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, response)

        output = _read_events(http_mocker, SyncMode.incremental, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == failure_type
        for fragment in message_fragments:
            assert fragment in error.message
        http_mocker.assert_number_of_calls(request, 1)


def test_410_updated_min_too_long_ago_is_transient():
    cursor = _days_ago(2)
    state = _partition_state(cursor)
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(updated_min=cursor), _error_response(410, "updatedMinTooLongAgo"))

        output = _read_events(http_mocker, SyncMode.incremental, state=state, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.transient_error
        assert "re-reads the calendar automatically" in error.message


@pytest.mark.parametrize("reason", ["deleted", "fullSyncRequired"])
def test_410_deleted_or_full_sync_required_is_config_error(reason):
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(), _error_response(410, reason, message="Resource has been deleted"))

        output = _read_events(http_mocker, SyncMode.incremental, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "no longer exists" in error.message and "reset the events stream" in error.message
