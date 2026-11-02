#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock-server tests for Google Calendar event sync tokens, pagination, filtering, and errors."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.interpolation.jinja import _ENVIRONMENT
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
_BASE_PARAMS = {"showDeleted": "true", "maxResults": "2500", "singleEvents": "false"}
_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
_COMMITTED_AT = "2026-10-16T00:00:00Z"


def _days_ago(n: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime(_DATETIME_FORMAT)


_RECORD = {"id": "e1", "updated": _days_ago(10)}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    # Backoff sleeps are skipped. The api_budget's own cool-down after a 429 would spin
    # without a real clock, so the 429 test disables budget updates explicitly.
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _events_request(sync_token: Optional[str] = None, page_token: Optional[str] = None) -> HttpRequest:
    params = dict(_BASE_PARAMS)
    if sync_token is not None:
        params["syncToken"] = sync_token
    if page_token is not None:
        params["pageToken"] = page_token
    return HttpRequest(_EVENTS_URL, query_params=params)


def _items_response(
    *records,
    next_page_token: Optional[str] = None,
    next_sync_token: Optional[str] = "tok1",
) -> HttpResponse:
    body: dict = {"items": list(records)}
    if next_page_token:
        body["nextPageToken"] = next_page_token
    elif next_sync_token is not None:
        body["nextSyncToken"] = next_sync_token
    return HttpResponse(json.dumps(body))


def _error_response(
    status_code: int,
    reason: Optional[str] = None,
    message: str = "error",
    body_code: Any = "status",
) -> HttpResponse:
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


def _sync_token_state(token: str):
    return (
        StateBuilder()
        .with_stream_state(
            "events",
            {"state_type": "sync_token", "token": token, "committed_at": _COMMITTED_AT},
        )
        .build()
    )


def _config(**overrides) -> Mapping[str, Any]:
    config = dict(_CONFIG)
    config.update(overrides)
    return config


def _read_events(http_mocker: HttpMocker, sync_mode: SyncMode, state=None, config=None, expecting_exception=False):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    config = config or _config()
    source = get_source(config, state=state)
    return read(source, config, _catalog(sync_mode), state=state, expecting_exception=expecting_exception)


def _stream_state(state_message) -> Mapping[str, Any]:
    return json.loads(json.dumps(state_message.state.stream.stream_state, default=lambda o: o.__dict__))


def _emitted_stream_states(output) -> list:
    return [_stream_state(message) for message in output.state_messages if message.state and message.state.stream]


def _record_ids(output) -> list:
    return [message.record.data["id"] for message in output.records]


def _error_trace(output):
    assert output.errors, "expected the sync to emit an error trace message"
    return output.errors[0].trace.error


def test_cold_read_commits_next_sync_token_only_after_the_last_page():
    first_page = _events_request()
    second_page = _events_request(page_token="page-2")
    first, second = {"id": "a", "updated": _days_ago(3)}, {"id": "b", "updated": _days_ago(2)}
    with HttpMocker() as http_mocker:
        http_mocker.get(first_page, _items_response(first, next_page_token="page-2"))
        http_mocker.get(second_page, _items_response(second, next_sync_token="tok1"))

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["a", "b"]
        assert {message.record.data["calendar_id"] for message in output.records} == {"primary"}
        states = _emitted_stream_states(output)
        assert states[-1]["state_type"] == "sync_token"
        assert states[-1]["token"] == "tok1"
        assert "committed_at" in states[-1]
        assert all(state.get("token") != "tok1" for state in states[:-1])
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


def test_warm_read_replays_sync_token_on_every_page_without_updated_min():
    first_page = _events_request(sync_token="tok0")
    second_page = _events_request(sync_token="tok0", page_token="page-2")
    state = _sync_token_state("tok0")
    first, second = {"id": "a", "updated": _days_ago(3)}, {"id": "b", "updated": _days_ago(2)}
    with HttpMocker() as http_mocker:
        http_mocker.get(first_page, _items_response(first, next_page_token="page-2"))
        http_mocker.get(second_page, _items_response(second, next_sync_token="tok2"))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert _record_ids(output) == ["a", "b"]
        assert _emitted_stream_states(output)[-1]["token"] == "tok2"
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


def test_legacy_datetime_state_restarts_without_a_sync_token():
    request = _events_request()
    legacy_state = StateBuilder().with_stream_state("events", {"updated": "2025-01-01T00:00:00.000000Z"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _items_response(_RECORD, next_sync_token="tok1"))

        output = _read_events(http_mocker, SyncMode.incremental, state=legacy_state)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        assert _emitted_stream_states(output)[-1]["token"] == "tok1"
        http_mocker.assert_number_of_calls(request, 1)


def test_start_date_filter_keeps_only_recent_events_and_stubs_without_updated():
    start_date = "2025-01-01T00:00:00Z"
    older = {"id": "older", "updated": "2024-12-31T23:59:59Z"}
    equal = {"id": "equal", "updated": "2025-01-01T00:00:00.000Z"}
    newer = {"id": "newer", "updated": "2025-01-01T00:00:01Z"}
    cancelled = {"id": "cancelled", "status": "cancelled"}
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _items_response(older, equal, newer, cancelled))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=start_date))

        assert output.errors == []
        assert _record_ids(output) == ["equal", "newer", "cancelled"]
        http_mocker.assert_number_of_calls(request, 1)


def test_cancelled_stub_is_stamped_with_frozen_current_time(monkeypatch):
    frozen_now = datetime(2026, 10, 19, 12, 34, 56, 789000, tzinfo=timezone.utc)
    monkeypatch.setitem(_ENVIRONMENT.globals, "now_utc", lambda: frozen_now)
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            _items_response({"id": "cancelled", "status": "cancelled"}, next_sync_token="tok1"),
        )

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert output.records[0].record.data["updated"] == frozen_now.strftime(_DATETIME_FORMAT)
        assert _emitted_stream_states(output)[-1]["token"] == "tok1"
        http_mocker.assert_number_of_calls(request, 1)


def test_no_start_date_emits_old_events_and_unedited_recurring_series():
    old_series = {
        "id": "weekly_since_2023",
        "updated": _days_ago(3 * 365),
        "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"],
        "status": "confirmed",
    }
    old_one_off = {"id": "old", "updated": _days_ago(5 * 365)}
    cancelled = {"id": "gone", "status": "cancelled"}
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _items_response(old_series, old_one_off, _RECORD, cancelled))

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["weekly_since_2023", "old", "e1", "gone"]
        http_mocker.assert_number_of_calls(request, 1)


def test_seconds_precision_updated_is_kept_by_start_date_filter():
    seconds_only = {
        "id": "s",
        "updated": (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _items_response(seconds_only))

        output = _read_events(http_mocker, SyncMode.incremental, config=_config(start_date=_days_ago(60)))

        assert output.errors == []
        assert _record_ids(output) == ["s"]
        assert output.records[0].record.data["updated"] == seconds_only["updated"]
        http_mocker.assert_number_of_calls(request, 1)


def test_record_updated_slightly_in_the_future_is_kept():
    skewed = {"id": "skewed", "updated": (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime(_DATETIME_FORMAT)}
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _items_response(skewed))

        output = _read_events(http_mocker, SyncMode.full_refresh)

        assert output.errors == []
        assert _record_ids(output) == ["skewed"]
        http_mocker.assert_number_of_calls(request, 1)


def test_rate_limit_403_retries_then_succeeds():
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, [_error_response(403, "userRateLimitExceeded"), _items_response(_RECORD)])

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 2)


@pytest.mark.parametrize("reason", [None, "rateLimitExceeded", "quotaExceeded"], ids=["no-reason", "rateLimitExceeded", "quotaExceeded"])
def test_429_retries_then_succeeds(monkeypatch, reason):
    monkeypatch.setattr(HttpAPIBudget, "update_from_response", lambda self, request, response: None)
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, [_error_response(429, reason), _items_response(_RECORD)])

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        http_mocker.assert_number_of_calls(request, 2)


@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_server_error_retries_then_succeeds(status_code):
    request = _events_request()
    with HttpMocker() as http_mocker:
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
    request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, response)

        output = _read_events(http_mocker, SyncMode.incremental, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == failure_type
        for fragment in message_fragments:
            assert fragment in error.message
        http_mocker.assert_number_of_calls(request, 1)


def test_410_full_sync_required_resets_token_and_commits_the_new_token():
    rejected_request = _events_request(sync_token="tok0")
    restarted_request = _events_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(rejected_request, _error_response(410, "fullSyncRequired"))
        http_mocker.get(restarted_request, _items_response(_RECORD, next_sync_token="tok1"))

        output = _read_events(http_mocker, SyncMode.incremental, state=_sync_token_state("tok0"))

        assert output.errors == []
        assert _record_ids(output) == ["e1"]
        assert _emitted_stream_states(output)[-1]["token"] == "tok1"
        http_mocker.assert_number_of_calls(rejected_request, 1)
        http_mocker.assert_number_of_calls(restarted_request, 1)


def test_410_deleted_is_a_config_error():
    request = _events_request(sync_token="tok0")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _error_response(410, "deleted", message="Resource has been deleted"))

        output = _read_events(
            http_mocker,
            SyncMode.incremental,
            state=_sync_token_state("tok0"),
            expecting_exception=True,
        )

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "no longer exists" in error.message
        http_mocker.assert_number_of_calls(request, 1)
