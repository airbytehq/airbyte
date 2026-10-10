#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
"""Runtime tests that load the declarative manifest through the CDK and verify
the incremental cursor, `start_date` server-side filtering, and rate-limit
backoff behaviour end-to-end.
"""

import json
import logging
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HTTPAPIBudget as HTTPAPIBudgetModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.call_rate import HttpAPIBudget
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import build_source


_MESSAGES_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
_DRAFTS_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
_LABELS_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/labels"
_THREADS_LIST_URL = "https://gmail.googleapis.com/gmail/v1/users/me/threads"
_PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"


def _read_stream(stream_name, sync_mode, config, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    state = StateBuilder().build() if not state else state
    return read(build_source(config, state), config, catalog, state)


def _gmail_calls(requests_mock, url_prefix):
    return [r for r in requests_mock.request_history if r.url.startswith(url_prefix)]


@pytest.fixture
def budget_ignores_429(mocker):
    """On a 429 the API budget marks its window as spent and waits for it to drain. With `time.sleep`
    mocked the window never drains, so tests of the retry logic stop the budget from reacting."""
    mocker.patch.object(HttpAPIBudget, "update_from_response")


def _stream_schema(config, stream_name):
    catalog = build_source(config).discover(logging.getLogger("test"), config)
    return next(stream.json_schema for stream in catalog.streams if stream.name == stream_name)


def _schema_at(schema, *path):
    """Walk properties (and array items) of a JSON schema; fails if a field on the path is undeclared."""
    node = schema
    for key in path:
        if "properties" not in node:
            node = node["items"]
        node = node["properties"][key]
    return node


def test_api_budget_weighs_each_call_by_its_gmail_quota_cost(manifest, base_config):
    # https://developers.google.com/workspace/gmail/api/reference/quota
    assert manifest["api_budget"]["policies"][0]["rates"] == [{"limit": 6000, "interval": "PT1M"}]
    budget = ModelToComponentFactory().create_component(HTTPAPIBudgetModel, manifest["api_budget"], base_config)
    expected = {
        "threads/t1": 40,
        "messages/m1": 20,
        "threads": 10,
        "messages": 5,
        "drafts": 5,
        "labels": 1,
        "labels/l1": 1,
        "profile": 1,
    }
    for path, weight in expected.items():
        request = requests.Request("GET", f"https://gmail.googleapis.com/gmail/v1/users/me/{path}?maxResults=100").prepare()
        assert budget.get_matching_policy(request).get_weight(request) == weight, path


def test_check_retries_profile_up_to_ten_times(base_config, requests_mock, mocker, budget_ignores_429):
    mocker.patch("time.sleep")
    rate_limited = {"status_code": 429, "headers": {"Retry-After": "0"}, "json": {"error": {"code": 429}}}
    requests_mock.get(_PROFILE_URL, [rate_limited] * 10 + [{"status_code": 200, "json": {"emailAddress": "user@example.com"}}])

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 11


def test_service_account_without_domain_wide_delegation_is_a_config_error(requests_mock):
    private_key = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        .private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        .decode()
    )
    service_account_info = {
        "type": "service_account",
        "client_email": "sa@project.iam.gserviceaccount.com",
        "private_key": private_key,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    config = {
        "credentials": {"auth_type": "Service", "service_account_info": json.dumps(service_account_info)},
        "include_spam_and_trash": False,
    }
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        status_code=401,
        json={"error": "unauthorized_client", "error_description": "Client is unauthorized to retrieve access tokens using this method."},
    )

    status = build_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert "unauthorized_client" in (status.message or "")
    assert not _gmail_calls(requests_mock, _PROFILE_URL)


def test_check_retries_profile_after_429(base_config, requests_mock, mocker, budget_ignores_429):
    mocker.patch("time.sleep")
    requests_mock.get(
        _PROFILE_URL,
        [
            {"status_code": 429, "headers": {"Retry-After": "0"}, "json": {"error": {"message": "rate limit"}}},
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2


def test_check_retries_profile_after_user_rate_limit_exceeded(base_config, requests_mock, mocker):
    mocker.patch("time.sleep")
    requests_mock.get(
        _PROFILE_URL,
        [
            {
                "status_code": 403,
                "headers": {"Retry-After": "0"},
                "json": {"error": {"errors": [{"reason": "userRateLimitExceeded"}]}},
            },
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2


@pytest.mark.parametrize(
    ("reason", "message"),
    [
        (
            "accessNotConfigured",
            "The Gmail API is not enabled for this Google Cloud project. Enable it at https://console.cloud.google.com/apis/library/gmail.googleapis.com and retry.",
        ),
        (
            "insufficientPermissions",
            "The authorized account lacks the required Gmail scope. Re-authenticate and grant gmail.readonly (service account or a refresh token you obtained yourself) or gmail.modify (the Authenticate your account flow).",
        ),
    ],
)
def test_gmail_api_configuration_errors_are_actionable(reason, message, base_config, requests_mock):
    error_response = {
        "status_code": 403,
        "json": {"error": {"errors": [{"reason": reason}]}},
    }
    requests_mock.get(_PROFILE_URL, [error_response, error_response])

    check_status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert check_status.status == Status.FAILED
    assert message in (check_status.message or "")
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 1, "a configuration error must not be retried"

    output = _read_stream("profile", SyncMode.full_refresh, base_config)

    assert not output.records
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2, "a configuration error must not be retried"
    assert any(
        msg.trace
        and msg.trace.error
        and msg.trace.error.failure_type
        and msg.trace.error.failure_type.value == "config_error"
        and message in msg.trace.error.message
        for msg in output.trace_messages
    )


def test_profile_read_emits_record(base_config, requests_mock):
    requests_mock.get(_PROFILE_URL, json={"emailAddress": "user@example.com", "historyId": "123"})

    output = _read_stream("profile", SyncMode.full_refresh, base_config)

    assert len(output.records) == 1


def test_labels_read_emits_records(base_config, requests_mock):
    color = {"backgroundColor": "#16a766", "textColor": "#ffffff"}
    requests_mock.get(_LABELS_LIST_URL, json={"labels": [{"id": "INBOX"}, {"id": "Label_1", "type": "user", "color": color}]})

    output = _read_stream("labels", SyncMode.full_refresh, base_config)

    assert [record.record.data.get("color") for record in output.records] == [None, color]
    schema = _stream_schema(base_config, "labels")
    assert "string" in _schema_at(schema, "color", "backgroundColor")["type"]
    assert "string" in _schema_at(schema, "color", "textColor")["type"]


def test_labels_details_reads_each_parent_partition(base_config, requests_mock):
    requests_mock.get(_LABELS_LIST_URL, json={"labels": [{"id": "label-1"}, {"id": "label-2"}]})
    color = {"backgroundColor": "#16a766", "textColor": "#ffffff"}
    requests_mock.get(f"{_LABELS_LIST_URL}/label-1", json={"id": "label-1", "messagesTotal": 2, "color": color})
    requests_mock.get(f"{_LABELS_LIST_URL}/label-2", json={"id": "label-2", "messagesTotal": 3})

    output = _read_stream("labels_details", SyncMode.full_refresh, base_config)

    assert len(output.records) == 2
    assert {record.record.data["id"]: record.record.data.get("color") for record in output.records} == {"label-1": color, "label-2": None}
    assert "string" in _schema_at(_stream_schema(base_config, "labels_details"), "color", "backgroundColor")["type"]
    child_paths = {urlparse(request.url).path for request in requests_mock.request_history if "/labels/" in urlparse(request.url).path}
    assert child_paths == {
        "/gmail/v1/users/me/labels/label-1",
        "/gmail/v1/users/me/labels/label-2",
    }


def test_threads_details_reads_each_parent_partition(base_config, requests_mock):
    requests_mock.get(_THREADS_LIST_URL, json={"threads": [{"id": "thread-1"}, {"id": "thread-2"}]})
    classification = [{"labelId": "cl-1", "fields": [{"fieldId": "f-1", "selection": "s-1"}]}]
    message_1 = {
        "id": "message-1",
        "classificationLabelValues": classification,
        "payload": {"body": {"attachmentId": "att-1", "size": 10}, "parts": [{"body": {"attachmentId": "att-2", "size": 20}}]},
    }
    requests_mock.get(f"{_THREADS_LIST_URL}/thread-1", json={"id": "thread-1", "messages": [message_1]})
    requests_mock.get(f"{_THREADS_LIST_URL}/thread-2", json={"id": "thread-2", "messages": [{"id": "message-2"}]})

    output = _read_stream("threads_details", SyncMode.full_refresh, base_config)

    assert len(output.records) == 2
    thread_1 = next(record.record.data for record in output.records if record.record.data["id"] == "thread-1")
    assert thread_1["messages"][0] == message_1
    schema = _stream_schema(base_config, "threads_details")
    assert "string" in _schema_at(schema, "messages", "classificationLabelValues", "fields", "selection")["type"]
    assert "string" in _schema_at(schema, "messages", "payload", "body", "attachmentId")["type"]
    assert "string" in _schema_at(schema, "messages", "payload", "parts", "body", "attachmentId")["type"]
    child_paths = {urlparse(request.url).path for request in requests_mock.request_history if "/threads/" in urlparse(request.url).path}
    assert child_paths == {
        "/gmail/v1/users/me/threads/thread-1",
        "/gmail/v1/users/me/threads/thread-2",
    }


@pytest.mark.parametrize(
    "path",
    [
        ("messages_details", "classificationLabelValues", "labelId"),
        ("messages_details", "classificationLabelValues", "fields", "fieldId"),
        ("messages_details", "payload", "body", "attachmentId"),
        ("messages_details", "payload", "parts", "body", "attachmentId"),
        ("threads_details", "messages", "classificationLabelValues", "labelId"),
        ("threads_details", "messages", "payload", "body", "attachmentId"),
        ("threads_details", "messages", "payload", "parts", "body", "attachmentId"),
    ],
)
def test_message_schemas_declare_gmail_fields(base_config, path):
    stream, *field_path = path
    assert "string" in _schema_at(_stream_schema(base_config, stream), *field_path)["type"]


def test_public_messages_standalone_is_full_refresh_and_emits_records(base_config, requests_mock):
    """Regression guard for the "messages cursor silently drops every record
    standalone" design flaw flagged in pnilan's follow-up review.

    If `messages` is ever re-declared as incremental on `internalDate`, the
    list-endpoint stubs (`{id, threadId}` with no cursor field) would be
    dropped by `DatetimeBasedCursor._is_within_daterange_boundaries`
    (returns False + WARN for records missing the cursor field). Users who
    select `messages` alone would then see zero records and a broken sync.

    The fix keeps `messages` as a public full-refresh stream; this test
    asserts the stubs are actually emitted when the stream is selected
    standalone, with no query-side `start_date` gate by default.
    """
    requests_mock.get(
        _MESSAGES_LIST_URL,
        json={"messages": [{"id": "m1", "threadId": "t1"}, {"id": "m2", "threadId": "t2"}]},
    )

    output = _read_stream("messages", SyncMode.full_refresh, base_config)

    assert len(output.records) == 2, (
        f"Public `messages` stream must emit list-endpoint stubs standalone; got {len(output.records)} records. "
        "If this regresses, `messages` has likely been re-declared as incremental on `internalDate` — which "
        "the list endpoint does not populate, so `DatetimeBasedCursor` would drop every record."
    )
    calls = _gmail_calls(requests_mock, _MESSAGES_LIST_URL)
    assert calls, "Expected at least one call to the messages list endpoint"
    qs = parse_qs(urlparse(calls[0].url).query)
    assert "q" not in qs or qs.get("q") == [
        ""
    ], f"Public `messages` must not inject a `q=after:` filter without a configured `start_date`; got {qs.get('q')!r}"


def test_public_messages_injects_after_unix_seconds_when_start_date_set(config_with_start_date, requests_mock):
    """Complement to the standalone test: when `start_date` IS configured,
    the public `messages` stream must still inject `q=after:<unix seconds>`
    (not the CDK's `MinMaxDatetime` default epoch), matching the
    drafts/threads behaviour.
    """
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages", SyncMode.full_refresh, config_with_start_date)

    calls = _gmail_calls(requests_mock, _MESSAGES_LIST_URL)
    assert calls, "Expected at least one call to the messages list endpoint"
    qs = parse_qs(urlparse(calls[0].url).query)
    assert qs.get("q") == ["after:1704067200"], f"Expected q=after:1704067200, got {qs.get('q')!r}"


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


def test_messages_details_parent_omits_q_when_no_start_date(base_config, requests_mock):
    """When `messages_details` runs with no configured `start_date`, the
    parent `messages` list call must not inject any `q=after:` filter.
    Pure declarative cannot bound the list call by the child's last-seen
    cursor (parent records lack `internalDate`, and there's no declarative
    state migration to copy the child cursor into a parent state), so we
    deliberately do NOT claim list-call bounding here. The `q` parameter
    must simply be absent (or empty) when no `start_date` is configured.
    """
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, base_config)

    list_calls = [c for c in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(c.url).path.endswith("/messages")]
    assert list_calls, "Expected at least one call to the messages list endpoint"
    qs = parse_qs(urlparse(list_calls[0].url).query)
    assert "q" not in qs or qs.get("q") == [
        ""
    ], f"Parent `messages` list call must not inject `q=after:` without a configured `start_date`; got {qs.get('q')!r}"


def test_messages_details_parent_injects_after_from_start_date(config_with_start_date, requests_mock):
    """With `start_date=2024-01-01T00:00:00Z` configured, the parent
    `messages` list call (driven by `messages_details`) must include
    `q=after:1704067200` (unix seconds) so Gmail filters server-side from
    the configured start date.
    """
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, config_with_start_date)

    list_calls = [c for c in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(c.url).path.endswith("/messages")]
    assert list_calls, "Expected at least one call to the messages list endpoint"
    qs = parse_qs(urlparse(list_calls[0].url).query)
    assert qs.get("q") == ["after:1704067200"], f"Expected q=after:1704067200, got {qs.get('q')!r}"


def test_messages_details_repeat_sync_state_is_continuous(base_config, requests_mock):
    """Repeat-sync regression: when a prior state cursor exists, the second
    sync must (a) preserve the prior cursor as a floor and (b) advance to
    the latest observed `internalDate`. This is the core guarantee
    incremental on `messages_details` provides — state continuity across
    syncs.

    What this test does NOT assert (and what we deliberately do not claim):
    the parent list call is NOT bounded by the prior cursor. Pure
    declarative cannot copy a child's cursor into a parent's state without
    a custom Python state migration; parent records (list stubs) lack
    `internalDate`, so the parent's own cursor cannot advance from
    observation. The reviewer's `incremental_dependency` regression check
    is therefore expressed here as a state-continuity assertion rather
    than a list-call-bound assertion. See manifest comments on
    `messages_details` for the full rationale.
    """
    # New messages observed on the second sync; both newer than prior cursor.
    requests_mock.get(
        _MESSAGES_LIST_URL,
        json={"messages": [{"id": "n1", "threadId": "t1"}, {"id": "n2", "threadId": "t2"}]},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/n1",
        json={"id": "n1", "threadId": "t1", "internalDate": "1700001000000", "snippet": "a"},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/n2",
        json={"id": "n2", "threadId": "t2", "internalDate": "1700002000000", "snippet": "b"},
    )

    # Seed prior state at the value the previous sync's checkpoint test
    # emitted (1700001000 unix seconds = 1700001000000 ms).
    prior_state = (
        StateBuilder()
        .with_stream_state(
            "messages_details",
            {"state": {"internalDate": "1700001000"}, "states": [], "lookback_window": 0},
        )
        .build()
    )
    output = _read_stream("messages_details", SyncMode.incremental, base_config, state=prior_state)

    # State must advance to the latest observed value, not regress to start_datetime.
    states = output.state_messages
    assert states, "Expected the second sync to emit state"
    final_state = states[-1].state.stream.stream_state.__dict__
    global_cursor = final_state.get("state", {}).get("internalDate")
    assert global_cursor == "1700002000", (
        f"Expected state to advance to max observed internalDate=1700002000; got {global_cursor!r}. "
        "If this regresses, the cursor is being reset on repeat syncs and incremental is broken."
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


def test_retry_after_on_429_is_honoured(base_config, requests_mock, mocker, budget_ignores_429):
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


@pytest.mark.parametrize("reason", ["rateLimitExceeded", "userRateLimitExceeded"])
def test_retry_after_on_403_rate_limit_exceeded_is_honoured(reason, base_config, requests_mock, mocker):
    """Gmail returns HTTP 403 with reason `rateLimitExceeded` or
    `userRateLimitExceeded` on quota-unit saturation (per
    https://developers.google.com/gmail/api/guides/handle-errors). Without an
    explicit response filter, the CDK's default error mapping would classify
    403 as FAIL/config_error and abort the sync. The manifest's second
    `HttpResponseFilter` re-classifies 403s whose `error.errors[0].reason`
    matches either documented marker as `RATE_LIMITED`, so the sync retries.

    Both reasons must be covered: a substring check `'rateLimitExceeded' in
    'userRateLimitExceeded'` evaluates to False (case-sensitive `R` vs `r`),
    so the predicate must use exact membership against the documented list.
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
                        "errors": [{"reason": reason, "message": "Rate Limit Exceeded"}],
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
    ), f"Expected a backoff honouring Retry-After=5s on 403 {reason}; got {sleep_durations!r}"
    assert output.records, f"Expected the retry to succeed and produce a record for reason={reason!r}"
    # Sanity: the sync must not have failed — a 403 without the predicate match
    # would have produced no records and an auth/config error trace.
    assert not any(
        "config_error" in (msg.trace.error.failure_type.value if msg.trace and msg.trace.error and msg.trace.error.failure_type else "")
        for msg in output.trace_messages
    ), f"403 {reason} must not be surfaced as a config_error"


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
