#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
"""Runtime tests that load the declarative manifest through the CDK and verify
the incremental cursor, `start_date` server-side filtering, and rate-limit
backoff behaviour end-to-end.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
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


def _messages_list_requests(requests_mock):
    messages_path = urlparse(_MESSAGES_LIST_URL).path
    return [r for r in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(r.url).path == messages_path]


def _config_starting_days_ago(config, days_ago):
    start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=days_ago)
    return {**config, "start_date": start.strftime("%Y-%m-%dT%H:%M:%SZ")}, int(start.timestamp())


def _message_list_query_bounds(request):
    query = parse_qs(urlparse(request.url).query)["q"][0]
    after, before = query.split()
    after_operator, after_value = after.split(":", 1)
    before_operator, before_value = before.split(":", 1)
    assert after_operator == "after"
    assert before_operator == "before"
    return query, int(after_value), int(before_value)


def _message_detail_paths(requests_mock, requests_since=0):
    messages_path = urlparse(_MESSAGES_LIST_URL).path
    return {
        urlparse(request.url).path
        for request in requests_mock.request_history[requests_since:]
        if urlparse(request.url).path.startswith(f"{messages_path}/")
    }


def _state_data(output):
    return output.state_messages[-1].state.stream.stream_state.__dict__


def _parent_listed_until(state):
    parent_state = state.get("parent_state", {}).get("messages_for_details", {})
    return parent_state.get("state", parent_state).get("_listed_until")


def test_messages_for_details_is_internal(manifest):
    assert "messages_for_details" in manifest["definitions"]["streams"]
    assert all(stream.get("name") != "messages_for_details" for stream in manifest["streams"])


def _retry_after_timestamp(seconds_from_now=120):
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds_from_now)).isoformat().replace("+00:00", "Z")


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


def _schema_nodes(schema, path=()):
    yield path, schema
    for key, subschema in schema.get("properties", {}).items():
        yield from _schema_nodes(subschema, path + (key,))
    if "items" in schema:
        yield from _schema_nodes(schema["items"], path + ("[]",))


_QUOTA_PATHS = ["threads/t1", "messages/m1", "threads", "messages", "drafts", "labels", "labels/l1", "profile"]


_OAUTH = {"auth_type": "Client", "client_id": "id", "client_secret": "secret", "client_refresh_token": "token"}
_SERVICE = {"auth_type": "Service", "service_account_info": "{}"}


@pytest.mark.parametrize(
    ("credentials", "limit", "weights"),
    [
        # https://developers.google.com/workspace/gmail/api/reference/quota
        # Airbyte's OAuth app is on a project that kept the pre-May-2026 quota and unit costs.
        pytest.param(_OAUTH, 15000, [10, 5, 10, 5, 5, 1, 1, 1], id="oauth"),
        # A legacy top-level config that has not been migrated into `credentials` yet is OAuth too.
        pytest.param(None, 15000, [10, 5, 10, 5, 5, 1, 1, 1], id="legacy_top_level_oauth"),
        # A service account's own project may be on the new quota; `get` without `format` is `full`.
        pytest.param(_SERVICE, 6000, [120, 60, 10, 5, 5, 1, 1, 1], id="service_account"),
    ],
)
def test_api_budget_weighs_each_call_by_its_gmail_quota_cost(credentials, limit, weights, manifest, base_config):
    config = {**base_config, "credentials": credentials} if credentials else base_config
    budget = ModelToComponentFactory().create_component(HTTPAPIBudgetModel, manifest["api_budget"], config)
    for path, weight in zip(_QUOTA_PATHS, weights):
        request = requests.Request("GET", f"https://gmail.googleapis.com/gmail/v1/users/me/{path}?maxResults=100").prepare()
        policy = budget.get_matching_policy(request)
        assert [rate.limit for rate in policy._bucket.rates] == [limit], path
        assert policy.get_weight(request) == weight, path


@pytest.mark.parametrize(
    ("credentials", "allowed_calls"),
    [
        pytest.param(_OAUTH, 3000, id="oauth"),
        pytest.param(_SERVICE, 100, id="service_account"),
    ],
)
def test_api_budget_waits_once_the_per_user_quota_is_spent(credentials, allowed_calls, manifest, base_config, mocker):
    sleep_mock = mocker.patch("time.sleep", side_effect=RuntimeError("budget blocked"))
    config = {**base_config, "credentials": credentials}
    budget = ModelToComponentFactory().create_component(HTTPAPIBudgetModel, manifest["api_budget"], config)
    request = requests.Request("GET", "https://gmail.googleapis.com/gmail/v1/users/me/messages/m1").prepare()

    for _ in range(allowed_calls):
        budget.acquire_call(request)
    sleep_mock.assert_not_called()

    with pytest.raises(RuntimeError, match="budget blocked"):
        budget.acquire_call(request)


_RATE_LIMITED = {"status_code": 429, "headers": {"Retry-After": "1"}, "json": {"error": {"code": 429}}}


def test_check_retries_profile_up_to_ten_times(base_config, requests_mock, mocker, budget_ignores_429):
    mocker.patch("time.sleep")
    requests_mock.get(_PROFILE_URL, [_RATE_LIMITED] * 10 + [{"status_code": 200, "json": {"emailAddress": "user@example.com"}}])

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 11


def test_check_fails_after_ten_retries(base_config, requests_mock, mocker, budget_ignores_429):
    mocker.patch("time.sleep")
    requests_mock.get(_PROFILE_URL, [_RATE_LIMITED] * 12)

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert status.status == Status.FAILED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 11


def _service_account_config():
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
    return {
        "credentials": {"auth_type": "Service", "service_account_info": json.dumps(service_account_info)},
        "include_spam_and_trash": False,
    }


@pytest.mark.parametrize(
    ("status_code", "error"),
    [(400, "invalid_grant"), (401, "invalid_client"), (401, "disabled_client"), (401, "deleted_client")],
)
def test_service_account_token_error_is_reported(status_code, error, requests_mock):
    config = _service_account_config()
    requests_mock.post("https://oauth2.googleapis.com/token", status_code=status_code, json={"error": error})

    status = build_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert f"Provider error: {error}" in (status.message or "")
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


def test_check_waits_for_retry_after_timestamp_in_429_body(base_config, requests_mock, mocker, budget_ignores_429):
    sleep_mock = mocker.patch("time.sleep")
    retry_at = _retry_after_timestamp()
    requests_mock.get(
        _PROFILE_URL,
        [
            {
                "status_code": 429,
                "json": {"error": {"code": 429, "message": f"User-rate limit exceeded. Retry after {retry_at}"}},
            },
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2
    assert any(115 <= duration <= 122 for duration in sleep_durations), sleep_durations


def test_check_waits_for_retry_after_timestamp_in_403_body(base_config, requests_mock, mocker, budget_ignores_429):
    sleep_mock = mocker.patch("time.sleep")
    retry_at = _retry_after_timestamp()
    requests_mock.get(
        _PROFILE_URL,
        [
            {
                "status_code": 403,
                "json": {
                    "error": {
                        "code": 403,
                        "message": f"User-rate limit exceeded. Retry after {retry_at}",
                        "errors": [{"message": "User-rate limit exceeded.", "reason": "rateLimitExceeded"}],
                        "status": "RESOURCE_EXHAUSTED",
                    }
                },
            },
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2
    assert any(115 <= duration <= 122 for duration in sleep_durations), sleep_durations


def test_check_uses_exponential_backoff_when_retry_after_is_missing(base_config, requests_mock, mocker, budget_ignores_429):
    sleep_mock = mocker.patch("time.sleep")
    requests_mock.get(
        _PROFILE_URL,
        [
            {"status_code": 429, "json": {"error": {"code": 429, "message": "User-rate limit exceeded."}}},
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2
    assert 11.0 in sleep_durations, sleep_durations


def test_check_fails_when_retry_after_exceeds_body_wait_cap(base_config, requests_mock, mocker, budget_ignores_429):
    mocker.patch("time.sleep")
    retry_at = _retry_after_timestamp(seconds_from_now=3600)
    requests_mock.get(
        _PROFILE_URL,
        status_code=429,
        json={"error": {"code": 429, "message": f"User-rate limit exceeded. Retry after {retry_at}"}},
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    assert status.status == Status.FAILED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 1
    assert "longer than the connector is allowed to wait" in (status.message or "")


def test_check_uses_one_second_floor_for_past_retry_after_timestamp(base_config, requests_mock, mocker, budget_ignores_429):
    sleep_mock = mocker.patch("time.sleep")
    retry_at = _retry_after_timestamp(seconds_from_now=-1)
    requests_mock.get(
        _PROFILE_URL,
        [
            {"status_code": 429, "json": {"error": {"message": f"User-rate limit exceeded. Retry after {retry_at}"}}},
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert status.status == Status.SUCCEEDED
    assert len(_gmail_calls(requests_mock, _PROFILE_URL)) == 2
    assert any(duration <= 2 for duration in sleep_durations), sleep_durations
    assert 11.0 not in sleep_durations


def test_check_uses_exponential_backoff_for_non_json_rate_limit_body(base_config, requests_mock, mocker, budget_ignores_429):
    sleep_mock = mocker.patch("time.sleep")
    requests_mock.get(
        _PROFILE_URL,
        [
            {"status_code": 429, "text": "Too many requests"},
            {"status_code": 200, "json": {"emailAddress": "user@example.com"}},
        ],
    )

    status = build_source(base_config).check(logging.getLogger("test"), base_config)

    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list if call.args]
    assert status.status == Status.SUCCEEDED
    assert 11.0 in sleep_durations, sleep_durations


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
        (
            "domainPolicy",
            "The Google Workspace administrator has disabled Gmail apps for this domain. Ask the administrator to allow Gmail API access for this app, then retry.",
        ),
    ],
)
def test_gmail_api_configuration_errors_are_actionable(reason, message, base_config, requests_mock):
    _assert_config_error_not_retried(403, reason, message, base_config, requests_mock)


def test_account_without_mailbox_is_a_config_error(base_config, requests_mock):
    _assert_config_error_not_retried(
        400,
        "failedPrecondition",
        "The authenticated account has no Gmail mailbox: either a service account, which has no mailbox of its own, or a Workspace user without Gmail enabled. Authenticate as the user whose mailbox you want to sync.",
        base_config,
        requests_mock,
    )


def _assert_config_error_not_retried(status_code, reason, message, base_config, requests_mock):
    error_response = {
        "status_code": status_code,
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


def test_profile_primary_key_and_integer_schema_types(base_config):
    source = build_source(base_config)
    catalog = source.discover(logging.getLogger("test"), base_config)
    discovered_streams = {stream.name: stream for stream in catalog.streams}
    assert discovered_streams["profile"].source_defined_primary_key == [["emailAddress"]]
    schemas = {stream.name: stream.json_schema for stream in catalog.streams}
    number_typed_paths = [
        (stream_name, path)
        for stream_name, schema in schemas.items()
        for path, node in _schema_nodes(schema)
        if "number" in (node.get("type") if isinstance(node.get("type"), list) else [node.get("type")])
    ]
    assert number_typed_paths == []

    expected_integer_paths = {
        "profile": {
            ("messagesTotal",),
            ("threadsTotal",),
        },
        "labels_details": {
            ("messagesTotal",),
            ("messagesUnread",),
            ("threadsTotal",),
            ("threadsUnread",),
        },
        "messages_details": {
            ("sizeEstimate",),
            ("payload", "body", "size"),
            ("payload", "parts", "[]", "body", "size"),
            ("payload", "parts", "[]", "parts", "[]", "body", "size"),
            ("payload", "parts", "[]", "parts", "[]", "parts", "[]", "body", "size"),
        },
        "threads_details": {
            ("messages", "[]", "sizeEstimate"),
            ("messages", "[]", "payload", "body", "size"),
            ("messages", "[]", "payload", "parts", "[]", "body", "size"),
            ("messages", "[]", "payload", "parts", "[]", "parts", "[]", "body", "size"),
            ("messages", "[]", "payload", "parts", "[]", "parts", "[]", "parts", "[]", "body", "size"),
        },
    }
    for stream_name, expected_paths in expected_integer_paths.items():
        integer_paths = set()
        for path, node in _schema_nodes(schemas[stream_name]):
            node_type = node.get("type")
            if node_type == "integer" or (isinstance(node_type, list) and "integer" in node_type):
                assert node_type == ["integer", "null"]
                integer_paths.add(path)
        assert integer_paths == expected_paths


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


@pytest.mark.parametrize(
    ("stream_name", "message_path"),
    [
        ("messages_details", ("payload",)),
        ("threads_details", ("messages", "payload")),
    ],
)
def test_message_part_schemas_declare_nested_parts(base_config, stream_name, message_path):
    schema = _stream_schema(base_config, stream_name)
    expected_properties = {"body", "filename", "headers", "mimeType", "partId"}

    for depth in (2, 3, 4):
        parts_schema = _schema_at(schema, *(message_path + ("parts",) * depth))
        assert {"array", "null"} <= set(parts_schema["type"])
        assert {"object", "null"} <= set(parts_schema["items"]["type"])

        if depth < 4:
            assert expected_properties <= set(parts_schema["items"]["properties"])
        else:
            assert "properties" not in parts_schema["items"]


def test_nested_message_part_schemas_match_between_detail_streams(base_config):
    messages_schema = _stream_schema(base_config, "messages_details")
    threads_schema = _stream_schema(base_config, "threads_details")

    assert _schema_at(messages_schema, "payload", "parts") == _schema_at(threads_schema, "messages", "payload", "parts")


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
    successful sync its cursor is the max `internalDate` in milliseconds,
    while the internal parent state tracks the list interval in Unix seconds.
    """
    config, start_epoch = _config_starting_days_ago(base_config, days_ago=5)
    first_cursor = str((start_epoch + 10) * 1000)
    second_cursor = str((start_epoch + 20) * 1000)

    # users.messages.list returns stubs only — this mirrors the real Gmail API.
    requests_mock.get(
        _MESSAGES_LIST_URL,
        json={"messages": [{"id": "m1", "threadId": "t1"}, {"id": "m2", "threadId": "t2"}]},
    )
    # users.messages.get populates internalDate on each message.
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        json={"id": "m1", "threadId": "t1", "internalDate": first_cursor, "snippet": "a"},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m2",
        json={"id": "m2", "threadId": "t2", "internalDate": second_cursor, "snippet": "b"},
    )

    output = _read_stream("messages_details", SyncMode.incremental, config)

    assert output.records, "Expected at least one record from messages_details"
    states = output.state_messages
    assert states, "Expected at least one state message — messages_details must be incremental"
    final_state = _state_data(output)
    global_state = final_state.get("state", {})
    cursor_value = global_state.get("internalDate")
    assert cursor_value == second_cursor, f"Expected max internalDate in milliseconds; got {final_state!r}"
    assert len(cursor_value) == 13
    partitions = final_state.get("states", [])
    assert partitions, "Expected at least one per-partition cursor entry"
    for entry in partitions:
        assert entry["cursor"].get("internalDate"), f"Expected each partition cursor to carry internalDate; got {entry!r}"
    parent_cursor = _parent_listed_until(final_state)
    assert parent_cursor is not None and len(parent_cursor) == 10
    assert int(parent_cursor) > 1080777600


def test_messages_details_parent_uses_default_start_date_when_none_configured(base_config, requests_mock):
    """Without a configured `start_date`, the parent list query starts at
    the connector's default date (2004-04-01T00:00:00Z).
    """
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, base_config)

    list_calls = [c for c in _gmail_calls(requests_mock, _MESSAGES_LIST_URL) if urlparse(c.url).path.endswith("/messages")]
    assert list_calls, "Expected at least one call to the messages list endpoint"
    query, after, before = _message_list_query_bounds(list_calls[0])
    assert query == "after:1080777600 before:1083369600"
    assert after == 1080777600
    assert before == 1083369600


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
    query, after, before = _message_list_query_bounds(list_calls[0])
    assert query == "after:1704067200 before:1706659200"
    assert after == 1704067200
    assert before == 1706659200


def test_messages_details_repeat_sync_state_is_continuous(base_config, requests_mock):
    """Repeat-sync regression: when a prior state cursor exists, the second
    sync must (a) preserve the prior cursor as a floor and (b) advance to
    the latest observed `internalDate`. This is the core guarantee
    incremental sync on `messages_details` provides — state continuity
    across syncs.
    """
    config, _ = _config_starting_days_ago(base_config, days_ago=3)
    prior_cursor = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp() * 1000)
    first_cursor = str(prior_cursor + 1000)
    second_cursor = str(prior_cursor + 2000)

    # New messages observed on the second sync; both newer than prior cursor.
    requests_mock.get(
        _MESSAGES_LIST_URL,
        json={"messages": [{"id": "n1", "threadId": "t1"}, {"id": "n2", "threadId": "t2"}]},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/n1",
        json={"id": "n1", "threadId": "t1", "internalDate": first_cursor, "snippet": "a"},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/n2",
        json={"id": "n2", "threadId": "t2", "internalDate": second_cursor, "snippet": "b"},
    )

    prior_state = (
        StateBuilder()
        .with_stream_state(
            "messages_details",
            {"state": {"internalDate": str(prior_cursor)}, "states": [], "lookback_window": 0},
        )
        .build()
    )
    output = _read_stream("messages_details", SyncMode.incremental, config, state=prior_state)

    # State must advance to the latest observed value, not regress to start_datetime.
    states = output.state_messages
    assert states, "Expected the second sync to emit state"
    final_state = states[-1].state.stream.stream_state.__dict__
    global_cursor = final_state.get("state", {}).get("internalDate")
    assert global_cursor == second_cursor, (
        f"Expected state to advance to max observed internalDate={second_cursor}; got {global_cursor!r}. "
        "If this regresses, the cursor is being reset on repeat syncs and incremental is broken."
    )


def test_messages_details_start_date_request_fetches_only_listed_ids(config_with_start_date, requests_mock):
    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {"json": {"messages": [{"id": "m1", "threadId": "t1"}]}},
            {"json": {"messages": []}},
        ],
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        json={"id": "m1", "threadId": "t1", "internalDate": "1704067201000"},
    )

    output = _read_stream("messages_details", SyncMode.incremental, config_with_start_date)

    query, after, before = _message_list_query_bounds(_messages_list_requests(requests_mock)[0])
    assert query == "after:1704067200 before:1706659200"
    assert after == 1704067200
    assert before == 1706659200
    assert parse_qs(urlparse(_messages_list_requests(requests_mock)[0].url).query).get("includeSpamTrash") == ["False"]
    assert len(output.records) == 1
    assert _message_detail_paths(requests_mock) == {f"{urlparse(_MESSAGES_LIST_URL).path}/m1"}


def test_messages_details_second_sync_uses_parent_state_and_round_trips_ms(base_config, requests_mock):
    config, _ = _config_starting_days_ago(base_config, days_ago=5)
    internal_date = str(int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp() * 1000))

    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {"json": {"messages": [{"id": "m1", "threadId": "t1"}]}},
            {"json": {"messages": [{"id": "m1", "threadId": "t1"}]}},
        ],
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        [
            {"json": {"id": "m1", "threadId": "t1", "internalDate": internal_date}},
            {"json": {"id": "m1", "threadId": "t1", "internalDate": internal_date}},
        ],
    )

    first = _read_stream("messages_details", SyncMode.incremental, config)
    first_state = _state_data(first)
    first_cursor = first_state["state"]["internalDate"]
    previous_end = _parent_listed_until(first_state)
    assert previous_end is not None and len(previous_end) == 10
    previous_end = int(previous_end)
    assert len(first_cursor) == 13
    state = StateBuilder().with_stream_state("messages_details", first_state).build()

    requests_before_second = len(requests_mock.request_history)
    second = _read_stream("messages_details", SyncMode.incremental, config, state=state)
    query, after, before = _message_list_query_bounds(_messages_list_requests(requests_mock)[-1])
    second_state = _state_data(second)

    assert after == previous_end - 3600
    second_parent_end = _parent_listed_until(second_state)
    assert second_parent_end is not None
    assert before == int(second_parent_end) + 1
    assert query == f"after:{previous_end - 3600} before:{before}"
    assert second_state["state"]["internalDate"] == first_cursor
    assert second_parent_end is not None and len(second_parent_end) == 10
    assert int(second_parent_end) >= previous_end
    assert _message_detail_paths(requests_mock, requests_before_second) == {f"{urlparse(_MESSAGES_LIST_URL).path}/m1"}
    assert [record.record.data["id"] for record in second.records] == ["m1"]


def test_messages_details_lookback_emits_mail_listed_late(base_config, requests_mock):
    """Gmail can list a message after a newer one has already been synced.
    The one-hour lookback must re-list and emit it even though its
    `internalDate` is older than the child cursor, and must re-emit the
    overlapping message rather than filter it out.
    """
    config, _ = _config_starting_days_ago(base_config, days_ago=5)
    now = datetime.now(timezone.utc)
    latest = str(int((now - timedelta(minutes=1)).timestamp() * 1000))
    late = str(int((now - timedelta(minutes=10)).timestamp() * 1000))
    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {"json": {"messages": [{"id": "m_latest", "threadId": "t1"}]}},
            {"json": {"messages": [{"id": "m_latest", "threadId": "t1"}, {"id": "m_late", "threadId": "t2"}]}},
        ],
    )
    requests_mock.get(f"{_MESSAGES_LIST_URL}/m_latest", json={"id": "m_latest", "threadId": "t1", "internalDate": latest})
    requests_mock.get(f"{_MESSAGES_LIST_URL}/m_late", json={"id": "m_late", "threadId": "t2", "internalDate": late})

    first = _read_stream("messages_details", SyncMode.incremental, config)
    first_state = _state_data(first)
    assert first_state["state"]["internalDate"] == latest
    state = StateBuilder().with_stream_state("messages_details", first_state).build()

    second = _read_stream("messages_details", SyncMode.incremental, config, state=state)

    assert sorted(record.record.data["id"] for record in second.records) == ["m_late", "m_latest"]
    assert _state_data(second)["state"]["internalDate"] == latest


def test_messages_details_parent_checkpoints_completed_slices_before_failed_child(base_config, requests_mock):
    config, start_epoch = _config_starting_days_ago(base_config, days_ago=75)
    step = 30 * 24 * 60 * 60
    first_slice_end = start_epoch + step - 1
    second_slice_end = start_epoch + 2 * step - 1
    third_slice_start = second_slice_end + 1
    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {"json": {"messages": [{"id": "slice-1", "threadId": "t1"}]}},
            {"json": {"messages": [{"id": "slice-2", "threadId": "t2"}]}},
            {"json": {"messages": [{"id": "slice-3", "threadId": "t3"}]}},
        ],
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/slice-1",
        json={"id": "slice-1", "threadId": "t1", "internalDate": str((start_epoch + 10) * 1000)},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/slice-2",
        json={"id": "slice-2", "threadId": "t2", "internalDate": str((start_epoch + step + 10) * 1000)},
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/slice-3",
        status_code=400,
        json={"error": {"code": 400, "message": "Invalid request"}},
    )
    state = StateBuilder().build()
    catalog = CatalogBuilder().with_stream("messages_details", SyncMode.incremental).build()

    output = read(build_source(config, state), config, catalog, state, expecting_exception=True)

    assert output.errors
    assert {path.rsplit("/", 1)[-1] for path in _message_detail_paths(requests_mock)} == {
        "slice-1",
        "slice-2",
        "slice-3",
    }

    list_calls = _messages_list_requests(requests_mock)
    assert len(list_calls) == 3
    queries = [_message_list_query_bounds(request) for request in list_calls]
    assert queries[0] == (f"after:{start_epoch} before:{first_slice_end + 1}", start_epoch, first_slice_end + 1)
    assert queries[1] == (
        f"after:{first_slice_end + 1} before:{second_slice_end + 1}",
        first_slice_end + 1,
        second_slice_end + 1,
    )
    assert queries[2][1] == third_slice_start
    assert queries[2][2] > third_slice_start

    emitted_states = [message.state.stream.stream_state.__dict__ for message in output.state_messages]
    assert emitted_states, "Expected emitted state messages after the child request failure"
    parent_cursors = [
        int(parent_cursor) for emitted_state in emitted_states if (parent_cursor := _parent_listed_until(emitted_state)) is not None
    ]
    assert parent_cursors
    assert list(dict.fromkeys(parent_cursors)) == [first_slice_end, second_slice_end]
    assert parent_cursors[-1] == second_slice_end
    assert all(parent_cursor < third_slice_start for parent_cursor in parent_cursors)


def test_messages_details_slice_queries_are_contiguous_epoch_seconds(base_config, requests_mock):
    config, start_epoch = _config_starting_days_ago(base_config, days_ago=75)
    step = 30 * 24 * 60 * 60
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, config)

    list_calls = _messages_list_requests(requests_mock)
    assert len(list_calls) == 3
    queries = [_message_list_query_bounds(request) for request in list_calls]
    assert queries[0][0] == f"after:{start_epoch} before:{start_epoch + step}"
    assert queries[1][0] == f"after:{start_epoch + step} before:{start_epoch + 2 * step}"
    assert queries[2][1] == queries[1][2]
    assert all(after < before for _, after, before in queries)


def test_messages_details_parent_follows_next_page_token(base_config, requests_mock):
    config, _ = _config_starting_days_ago(base_config, days_ago=5)
    internal_date = str(int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000))
    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {"json": {"messages": [{"id": "m1", "threadId": "t1"}], "nextPageToken": "page-2"}},
            {"json": {"messages": [{"id": "m2", "threadId": "t2"}]}},
        ],
    )
    for message_id in ("m1", "m2"):
        requests_mock.get(
            f"{_MESSAGES_LIST_URL}/{message_id}",
            json={"id": message_id, "threadId": "t1", "internalDate": internal_date},
        )

    output = _read_stream("messages_details", SyncMode.incremental, config)

    list_calls = _messages_list_requests(requests_mock)
    assert len(list_calls) == 2
    first_params = parse_qs(urlparse(list_calls[0].url).query)
    second_params = parse_qs(urlparse(list_calls[1].url).query)
    assert "pageToken" not in first_params
    assert second_params["pageToken"] == ["page-2"]
    assert first_params["maxResults"] == second_params["maxResults"] == ["500"]
    assert first_params["q"] == second_params["q"]
    assert sorted(record.record.data["id"] for record in output.records) == ["m1", "m2"]


@pytest.mark.parametrize(
    ("stream_name", "list_url", "response_key"),
    [
        ("messages", _MESSAGES_LIST_URL, "messages"),
        ("threads", _THREADS_LIST_URL, "threads"),
        ("drafts", _DRAFTS_LIST_URL, "drafts"),
    ],
)
def test_list_streams_request_500_items_per_page(stream_name, list_url, response_key, base_config, requests_mock):
    requests_mock.get(list_url, json={response_key: [{"id": "stub"}]})

    _read_stream(stream_name, SyncMode.full_refresh, base_config)

    list_calls = [request for request in _gmail_calls(requests_mock, list_url) if urlparse(request.url).path == urlparse(list_url).path]
    assert len(list_calls) == 1
    assert parse_qs(urlparse(list_calls[0].url).query)["maxResults"] == ["500"]


@pytest.mark.parametrize("include_spam_and_trash, expected", [(False, "False"), (True, "True")])
def test_messages_details_parent_passes_include_spam_trash(include_spam_and_trash, expected, config_with_start_date, requests_mock):
    config = {**config_with_start_date, "include_spam_and_trash": include_spam_and_trash}
    requests_mock.get(_MESSAGES_LIST_URL, json={"messages": []})

    _read_stream("messages_details", SyncMode.incremental, config)

    list_calls = _messages_list_requests(requests_mock)
    assert list_calls
    assert all(parse_qs(urlparse(call.url).query)["includeSpamTrash"] == [expected] for call in list_calls)


def test_messages_details_full_refresh_reads_all_listed_ids(base_config, requests_mock):
    config, _ = _config_starting_days_ago(base_config, days_ago=5)
    internal_date = str(int(datetime.now(timezone.utc).timestamp() * 1000))
    requests_mock.get(
        _MESSAGES_LIST_URL,
        json={"messages": [{"id": "m1", "threadId": "t1"}, {"id": "m2", "threadId": "t2"}]},
    )
    for message_id in ("m1", "m2"):
        requests_mock.get(
            f"{_MESSAGES_LIST_URL}/{message_id}",
            json={"id": message_id, "threadId": "t1", "internalDate": internal_date},
        )

    output = _read_stream("messages_details", SyncMode.full_refresh, config)

    assert len(output.records) == 2
    assert _message_detail_paths(requests_mock) == {
        f"{urlparse(_MESSAGES_LIST_URL).path}/m1",
        f"{urlparse(_MESSAGES_LIST_URL).path}/m2",
    }


@pytest.mark.parametrize(
    "legacy_state",
    [
        pytest.param(
            {
                "state": {"internalDate": "1792710"},
                "parent_state": {},
                "lookback_window": 1173,
                "use_global_cursor": True,
            },
            id="global_cursor",
        ),
        pytest.param(
            {
                "state": {"internalDate": "1792710"},
                "states": [
                    {"partition": {"message_id": "m0", "parent_slice": {}}, "cursor": {"internalDate": "1792710"}},
                ],
                "parent_state": {},
                "lookback_window": 1173,
                "use_global_cursor": False,
            },
            id="per_partition",
        ),
    ],
)
def test_messages_details_legacy_truncated_state_reads_from_start_date(legacy_state, config_with_start_date, requests_mock):
    requests_mock.get(
        _MESSAGES_LIST_URL,
        [
            {"json": {"messages": [{"id": "m1", "threadId": "t1"}]}},
            {"json": {"messages": []}},
        ],
    )
    requests_mock.get(
        f"{_MESSAGES_LIST_URL}/m1",
        json={"id": "m1", "threadId": "t1", "internalDate": "1704067201000"},
    )
    state = StateBuilder().with_stream_state("messages_details", legacy_state).build()

    output = _read_stream("messages_details", SyncMode.incremental, config_with_start_date, state=state)

    query, after, before = _message_list_query_bounds(_messages_list_requests(requests_mock)[0])
    assert query == "after:1704067200 before:1706659200"
    assert after == 1704067200
    assert before == 1706659200
    assert len(output.records) == 1


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
