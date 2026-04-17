#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
"""Runtime tests that load the declarative manifest through the CDK and verify
the incremental cursor, `start_date` server-side filtering, and rate-limit
backoff behaviour end-to-end.
"""

from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import build_source


_MESSAGES_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
_DRAFTS_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
_THREADS_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/threads"


def _read_stream(stream_name, sync_mode, config, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    state = StateBuilder().build() if not state else state
    return read(build_source(config, state), config, catalog, state)


def _gmail_calls(requests_mock, url_prefix):
    return [r for r in requests_mock.request_history if r.url.startswith(url_prefix)]


def test_messages_details_checkpoints_on_internal_date(base_config, requests_mock):
    """`messages_details` owns the cursor because `internalDate` is only
    returned by `users.messages.get`, not by `users.messages.list`. After a
    successful sync the state must be the max `internalDate` (unix seconds)
    across the detail responses.
    """
    # users.messages.list returns stubs only — this mirrors the real Gmail API.
    requests_mock.get(
        _MESSAGES_LIST_URL,
        json={"messages": [{"id": "m1", "threadId": "t1"}, {"id": "m2", "threadId": "t2"}]},
    )
    # users.messages.get populates internalDate on each message.
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        json={"id": "m1", "threadId": "t1", "internalDate": "1700000000000", "snippet": "a"},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m2",
        json={"id": "m2", "threadId": "t2", "internalDate": "1700001000000", "snippet": "b"},
    )

    output = _read_stream("messages_details", SyncMode.incremental, base_config)

    assert output.records, "Expected at least one record from messages_details"
    states = output.state_messages
    assert states, "Expected at least one state message — messages_details must be incremental"
    # The concurrent per-partition cursor stores the global max under
    # `state.internalDate` once all partitions have emitted at least one value.
    final_state = states[-1].state.stream.stream_state.__dict__
    # datetime_format is "%s" so state is stored as unix seconds.
    global_state = final_state.get("state", {})
    cursor_value = global_state.get("internalDate")
    assert cursor_value == "1700001000", f"Expected max internalDate (unix s) under state.state.internalDate; got {final_state!r}"
    # Per-partition cursors must also each carry an `internalDate`.
    partitions = final_state.get("states", [])
    assert partitions, "Expected at least one per-partition cursor entry"
    for entry in partitions:
        assert entry["cursor"].get("internalDate"), f"Expected each partition cursor to carry internalDate; got {entry!r}"


def test_messages_parent_defaults_to_pre_gmail_epoch_when_no_start_date(base_config, requests_mock):
    """With no configured `start_date` and no prior state, the parent
    `messages` list call uses its cursor's `start_datetime` default
    (2004-04-01T00:00:00Z → unix 1080777600). That date predates Gmail, so
    the filter is effectively a no-op for real mailboxes — but it must be
    present so subsequent syncs can advance it via cursor state.
    """
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, base_config)

    list_calls = [c for c in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(c.url).path.endswith("/messages")]
    assert list_calls, "Expected at least one call to the messages list endpoint"
    qs = parse_qs(urlparse(list_calls[0].url).query)
    assert qs.get("q") == [
        "after:1080777600"
    ], f"Expected q=after:1080777600 (2004-04-01 unix seconds) when no start_date and no state; got {qs.get('q')!r}"


def test_messages_request_injects_after_from_start_date(config_with_start_date, requests_mock):
    """With `start_date=2024-01-01T00:00:00Z` and no prior state, the parent
    `messages` list call must include `q=after:1704067200` (unix seconds) so
    Gmail filters server-side."""
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, config_with_start_date)

    list_calls = [c for c in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(c.url).path.endswith("/messages")]
    assert list_calls, "Expected at least one call to the messages list endpoint"
    qs = parse_qs(urlparse(list_calls[0].url).query)
    assert qs.get("q") == ["after:1704067200"], f"Expected q=after:1704067200, got {qs.get('q')!r}"


def test_messages_parent_q_advances_with_prior_state(base_config, requests_mock):
    """When prior state carries `internalDate` (unix seconds), the parent
    `messages` list call must bound its `q=after:` to that cursor value — not
    to `start_date` or the default epoch. This proves `incremental_dependency:
    true` on the child's `ParentStreamConfig` actually migrates state to the
    parent's own cursor, making repeat syncs cheap.
    """
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    # A real second sync would receive the state emitted at the end of the
    # first sync. `incremental_dependency: true` captures the parent's cursor
    # under `parent_state.messages.internalDate`; this is what drives the
    # parent's `q=after:` on resume.
    prior_state = (
        StateBuilder()
        .with_stream_state(
            "messages_details",
            {
                "state": {"internalDate": "1725000000"},
                "states": [],
                "parent_state": {"messages": {"internalDate": "1725000000"}},
                "lookback_window": 0,
            },
        )
        .build()
    )
    _read_stream("messages_details", SyncMode.incremental, base_config, state=prior_state)

    list_calls = [c for c in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(c.url).path.endswith("/messages")]
    assert list_calls, "Expected at least one call to the messages list endpoint"
    # Every list call must be bounded by the prior cursor value.
    for call in list_calls:
        qs = parse_qs(urlparse(call.url).query)
        assert qs.get("q") == ["after:1725000000"], (
            f"Expected q=after:1725000000 from prior state, got {qs.get('q')!r}. "
            f"This indicates incremental_dependency did not migrate child state to the parent."
        )


def test_drafts_injects_after_unix_seconds_when_start_date_set(config_with_start_date, requests_mock):
    """Gmail's search grammar interprets `after:YYYY/MM/DD` as midnight PST,
    so we must use unix seconds to avoid an 8h drift. With
    `start_date=2024-01-01T00:00:00Z`, the request must include
    `q=after:1704067200`.
    """
    requests_mock.get(_DRAFTS_LIST_URL, json={"drafts": []})

    _read_stream("drafts", SyncMode.full_refresh, config_with_start_date)

    calls = _gmail_calls(requests_mock, _DRAFTS_LIST_URL)
    assert calls, "Expected at least one call to the drafts endpoint"
    qs = parse_qs(urlparse(calls[0].url).query)
    assert qs.get("q") == ["after:1704067200"], f"Expected q=after:1704067200, got {qs.get('q')!r}"


def test_threads_injects_after_unix_seconds_when_start_date_set(config_with_start_date, requests_mock):
    """Same as drafts — threads must also use unix seconds to avoid PST drift."""
    requests_mock.get(_THREADS_LIST_URL, json={"threads": []})

    _read_stream("threads", SyncMode.full_refresh, config_with_start_date)

    calls = _gmail_calls(requests_mock, _THREADS_LIST_URL)
    assert calls, "Expected at least one call to the threads endpoint"
    qs = parse_qs(urlparse(calls[0].url).query)
    assert qs.get("q") == ["after:1704067200"], f"Expected q=after:1704067200, got {qs.get('q')!r}"


def test_retry_after_on_429_is_honoured(base_config, requests_mock, mocker):
    """When Gmail returns a 429 with a `Retry-After` header, the
    `DefaultErrorHandler` on `base_requester` (with `WaitTimeFromHeader`
    backoff) must sleep for that duration and then retry the request.
    """
    sleep_mock = mocker.patch("time.sleep")

    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {
                "status_code": 429,
                "headers": {"Retry-After": "7"},
                "json": {"error": {"code": 429, "message": "rateLimitExceeded"}},
            },
            {
                "status_code": 200,
                "json": {"messages": [{"id": "m1", "threadId": "t1"}]},
            },
        ],
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        json={"id": "m1", "threadId": "t1", "internalDate": "1700000000000", "snippet": "a"},
    )

    output = _read_stream("messages_details", SyncMode.full_refresh, base_config)

    # The CDK's WaitTimeFromHeader honours the Retry-After header (with a small
    # safety padding); the resulting sleep must be at least the header value.
    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert any(7 <= duration <= 10 for duration in sleep_durations), f"Expected a backoff honouring Retry-After=7s; got {sleep_durations!r}"
    assert output.records, "Expected the retry to succeed and produce a record"


def test_retry_after_on_403_rate_limit_exceeded_is_honoured(base_config, requests_mock, mocker):
    """Gmail returns HTTP 403 with reason `rateLimitExceeded` or
    `userRateLimitExceeded` on quota-unit saturation (per
    https://developers.google.com/gmail/api/guides/handle-errors). Without an
    explicit response filter, the CDK's default error mapping would classify
    403 as FAIL/config_error and abort the sync. The manifest's second
    `HttpResponseFilter` re-classifies 403s whose body carries the
    `rateLimitExceeded` marker as `RATE_LIMITED`, so the sync retries instead.
    """
    sleep_mock = mocker.patch("time.sleep")

    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {
                "status_code": 403,
                "headers": {"Retry-After": "5"},
                "json": {
                    "error": {
                        "code": 403,
                        "message": "User-rate limit exceeded.",
                        "errors": [{"reason": "rateLimitExceeded", "message": "Rate Limit Exceeded"}],
                    }
                },
            },
            {
                "status_code": 200,
                "json": {"messages": [{"id": "m1", "threadId": "t1"}]},
            },
        ],
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        json={"id": "m1", "threadId": "t1", "internalDate": "1700000000000", "snippet": "a"},
    )

    output = _read_stream("messages_details", SyncMode.full_refresh, base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert any(
        5 <= duration <= 8 for duration in sleep_durations
    ), f"Expected a backoff honouring Retry-After=5s on 403 rateLimitExceeded; got {sleep_durations!r}"
    assert output.records, "Expected the retry to succeed and produce a record"
    # Sanity: the sync must not have failed — a 403 without the rateLimitExceeded
    # filter would have produced no records and an auth/config error trace.
    assert not any(
        "config_error" in (msg.trace.error.failure_type.value if msg.trace and msg.trace.error and msg.trace.error.failure_type else "")
        for msg in output.trace_messages
    ), "403 rateLimitExceeded must not be surfaced as a config_error"


def test_non_rate_limit_403_is_not_retried(base_config, requests_mock, mocker):
    """Negative guard for the `rateLimitExceeded` predicate.

    A 403 whose `error.errors[0].reason` is *not* `rateLimitExceeded`
    (e.g. insufficient OAuth scope, disabled Gmail API, revoked token)
    must stay classified as FAIL/config_error by the CDK default
    mapping. A bug in the predicate (or using `http_codes: [403]` alone,
    which is OR'd with the predicate inside `HttpResponseFilter`) would
    reclassify every 403 as `RATE_LIMITED` and retry indefinitely,
    masking auth failures that should fail fast.
    """
    sleep_mock = mocker.patch("time.sleep")

    requests_mock.get(
        _MESSAGES_LIST_URL,
        status_code=403,
        headers={"Retry-After": "5"},
        json={
            "error": {
                "code": 403,
                "message": "Request had insufficient authentication scopes.",
                "errors": [
                    {
                        "reason": "insufficientPermissions",
                        "message": "Insufficient Permission",
                    }
                ],
                "status": "PERMISSION_DENIED",
            }
        },
    )

    output = _read_stream("messages_details", SyncMode.full_refresh, base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert not any(
        d >= 5 for d in sleep_durations
    ), f"Insufficient-permission 403 must not trigger a Retry-After backoff; got {sleep_durations!r}"
    assert not output.records, "Insufficient-permission 403 must not yield records"
