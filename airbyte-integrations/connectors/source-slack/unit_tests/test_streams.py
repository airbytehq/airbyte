#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from unittest.mock import MagicMock, Mock

import pytest
from requests import Response

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_retriever, get_source, get_stream_by_name


@pytest.fixture
def authenticator(token_config):
    return TokenAuthenticator(token_config["credentials"]["api_token"])


@pytest.mark.parametrize(
    "start_date, end_date, messages, stream_state, expected_result",
    (
        (
            "2020-01-01T00:00:00Z",
            "2020-01-02T00:00:00Z",
            [{"ts": 1577866844, "reply_count": 1}, {"ts": 1577877406, "reply_count": 1}],
            {},
            [
                {
                    "float_ts": 1577866844,
                    "parent_slice": {"channel": "airbyte-for-beginners", "parent_slice": {}},
                    "start_time": "1626984000",
                    "end_time": "1627070400",
                },
                {
                    "float_ts": 1577877406,
                    "parent_slice": {"channel": "airbyte-for-beginners", "parent_slice": {}},
                    "start_time": "1626984000",
                    "end_time": "1627070400",
                },
                {
                    "float_ts": 1577866844,
                    "parent_slice": {"channel": "good-reads", "parent_slice": {}},
                    "start_time": "1626984000",
                    "end_time": "1627070400",
                },
                {
                    "float_ts": 1577877406,
                    "parent_slice": {"channel": "good-reads", "parent_slice": {}},
                    "start_time": "1626984000",
                    "end_time": "1627070400",
                },
            ],
        ),
        # TODO: uncomment this when requests cache issue is resolved
        # ("2020-01-02T00:00:00Z", "2020-01-01T00:00:00Z", [], {}, []),
    ),
)
def test_threads_stream_slices(requests_mock, authenticator, token_config, start_date, end_date, messages, stream_state, expected_result):
    token_config["channel_filter"] = []

    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [{"json": {"messages": messages}}, {"json": {"messages": []}}],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [{"json": {"messages": messages}}, {"json": {"messages": []}}],
    )

    stream = get_stream_by_name("threads", token_config)
    slices = list(map(lambda partition: partition.to_slice(), stream.generate_partitions()))

    assert len(slices) == len(expected_result)
    for s in slices:
        assert s in expected_result


@pytest.mark.parametrize(
    "current_state, latest_record, expected_state",
    (
        ({}, {"ts": 1507866844}, {"float_ts": "1626984000"}),
        ({}, {"ts": 1726984000}, {"float_ts": "1726984000"}),
        ({"float_ts": 1588866844}, {"ts": 1626984010}, {"float_ts": "1626984010"}),
        ({"float_ts": 1577800844}, {"ts": 1626984010}, {"float_ts": "1626984010"}),
    ),
)
def test_get_updated_state(requests_mock, authenticator, token_config, current_state, latest_record, expected_state):
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [{"json": {"messages": [{"ts": 1507866847, "reply_count": 1}]}}, {"json": {"messages": []}}],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [{"json": {"messages": [{"ts": 1507866847, "reply_count": 1}]}}, {"json": {"messages": []}}],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies?channel=good-reads&limit=1000&ts=1507866847",
        [{"json": {"messages": [latest_record]}}, {"json": {"messages": []}}],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies?channel=airbyte-for-beginners&limit=1000&ts=1507866847",
        [{"json": {"messages": [latest_record]}}, {"json": {"messages": []}}],
    )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "threads", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state("threads", current_state).build()
    source_slack = get_source(token_config, "threads", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert output.records
    assert output.most_recent_state.stream_state.state == expected_state


def test_threads_request_params(authenticator, token_config):
    stream = get_stream_by_name("threads", token_config)
    threads_slice = {"parent_slice": {"channel": "airbyte-for-beginners"}}
    assert get_retriever(stream).requester.get_request_params(stream_slice=threads_slice, next_page_token={}) == {
        "channel": "airbyte-for-beginners"
    }


def test_threads_parse_response(requests_mock, authenticator, token_config):
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [{"json": {"messages": [{"ts": 1507866847, "reply_count": 1}]}}, {"json": {"messages": []}}],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [{"json": {"messages": [{"ts": 1507866847, "reply_count": 1}]}}, {"json": {"messages": []}}],
    )

    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies?channel=airbyte-for-beginners&limit=1000&ts=1507866847",
        [
            {
                "json": {
                    "messages": [
                        {
                            "type": "message",
                            "user": "U061F7AUR",
                            "text": "island",
                            "thread_ts": "1482960137.003543",
                            "reply_count": 3,
                            "subscribed": True,
                            "last_read": "1484678597.521003",
                            "unread_count": 0,
                            "ts": "1482960137.003543",
                        }
                    ]
                }
            },
            {"json": {"messages": []}},
        ],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies?channel=good-reads&limit=1000&ts=1507866847",
        [
            {"json": {}},
        ],
    )

    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "threads", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state("threads", {}).build()
    source_slack = get_source(token_config, "threads", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    actual_response = output.records
    assert len(actual_response) == 1
    assert actual_response[0].record.data["float_ts"] == 1482960137.003543
    assert actual_response[0].record.data["channel_id"] == "airbyte-for-beginners"


@pytest.mark.parametrize("headers, expected_result", (({"Retry-After": "15"}, 1),))
def test_backoff(requests_mock, token_config, authenticator, headers, expected_result):
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies?channel=airbyte-for-beginners&limit=1000&ts=1507866847",
        [
            {"json": {"message": "rate limited"}, "headers": headers, "status_code": 429},
            {
                "status_code": 200,
                "json": {
                    "messages": [
                        {
                            "type": "message",
                            "user": "U061F7AUR",
                            "text": "island",
                            "thread_ts": "1482960137.003543",
                            "reply_count": 3,
                            "subscribed": True,
                            "last_read": "1484678597.521003",
                            "unread_count": 0,
                            "ts": "1482960137.003543",
                        }
                    ]
                },
            },
        ],
    )
    requests_mock.get(
        url="https://slack.com/api/conversations.replies?channel=good-reads&limit=1000&ts=1507866847",
        status_code=200,
        json={"json": {"messages": []}},
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [{"json": {"messages": [{"ts": 1507866847, "reply_count": 1}]}}, {"json": {"messages": []}}],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [{"json": {"messages": [{"ts": 1507866847, "reply_count": 1}]}}, {"json": {"messages": []}}],
    )

    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "threads", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state("threads", {}).build()
    source_slack = get_source(token_config, "threads", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert len([log.log.message for log in output.logs if "Retrying. Sleeping for 15.0 seconds" == log.log.message]) == 1
    assert len(output.records) == expected_result


def test_threads_stream_skips_messages_without_replies_when_enabled(requests_mock, token_config):
    """
    Verify that when threads_ignore_no_replies=True, the threads stream only creates
    partitions for parent messages with reply_count > 0.
    Messages with reply_count=0 or missing reply_count should be filtered out.
    """
    token_config["channel_filter"] = []
    token_config["threads_ignore_no_replies"] = True

    # Channel 1: one message with replies, one with reply_count=0, one with reply_count=None
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [
            {
                "json": {
                    "messages": [
                        {"ts": 1577866844, "reply_count": 3},
                        {"ts": 1577877406, "reply_count": 0},
                        {"ts": 1577888888, "reply_count": None},
                    ]
                }
            },
            {"json": {"messages": []}},
        ],
    )
    # Channel 2: one message with missing reply_count key entirely (should be filtered)
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [
            {"json": {"messages": [{"ts": 1577866844}]}},
            {"json": {"messages": []}},
        ],
    )

    stream = get_stream_by_name("threads", token_config)
    slices = list(map(lambda partition: partition.to_slice(), stream.generate_partitions()))

    # Only the message with reply_count=3 should produce a partition
    # reply_count=0, reply_count=None, and missing reply_count should all be filtered out
    assert len(slices) == 1
    assert slices[0]["float_ts"] == 1577866844
    assert slices[0]["parent_slice"]["channel"] == "airbyte-for-beginners"


def test_threads_stream_includes_all_messages_by_default(requests_mock, token_config):
    """
    Verify that when threads_ignore_no_replies is not set (default=False),
    all messages are passed through as partitions, preserving current behavior.
    This includes messages with reply_count=None (null from API).
    """
    token_config["channel_filter"] = []
    # Do NOT set threads_ignore_no_replies — should default to False

    # Channel 1: messages with various reply_count values including None
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [
            {
                "json": {
                    "messages": [
                        {"ts": 1577866844, "reply_count": 3},
                        {"ts": 1577877406, "reply_count": 0},
                        {"ts": 1577888888, "reply_count": None},
                    ]
                }
            },
            {"json": {"messages": []}},
        ],
    )
    # Channel 2: one message with missing reply_count key
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [
            {"json": {"messages": [{"ts": 1577866844}]}},
            {"json": {"messages": []}},
        ],
    )

    stream = get_stream_by_name("threads", token_config)
    slices = list(map(lambda partition: partition.to_slice(), stream.generate_partitions()))

    # All 4 messages should produce partitions (no filtering when disabled)
    assert len(slices) == 4


def test_threads_stream_no_replies_api_calls_skipped_when_enabled(requests_mock, token_config):
    """
    End-to-end test: when threads_ignore_no_replies=True, verify that conversations.replies
    is only called for messages with reply_count > 0 (not for reply_count=0, None, or absent).
    Uses requests_mock.request_history to confirm API call reduction.
    """
    token_config["channel_filter"] = []
    token_config["threads_ignore_no_replies"] = True

    # Channel 1: one message with replies (reply_count=3), one without (reply_count=0)
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [
            {
                "json": {
                    "messages": [
                        {"ts": "1577866844.000000", "reply_count": 3},
                        {"ts": "1577877406.000000", "reply_count": 0},
                    ]
                }
            },
            {"json": {"messages": []}},
        ],
    )
    # Channel 2: one message with reply_count=None (should be filtered)
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [
            {"json": {"messages": [{"ts": "1577866844.000000", "reply_count": None}]}},
            {"json": {"messages": []}},
        ],
    )
    # Only the message with reply_count=3 should trigger a conversations.replies call
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies?channel=airbyte-for-beginners&limit=1000&ts=1577866844.000000",
        json={
            "messages": [
                {
                    "type": "message",
                    "ts": "1577866844.000000",
                    "thread_ts": "1577866844.000000",
                    "reply_count": 3,
                    "text": "parent",
                },
                {
                    "type": "message",
                    "ts": "1577866845.000000",
                    "thread_ts": "1577866844.000000",
                    "text": "reply",
                },
            ]
        },
    )

    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {
                        "name": "threads",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state("threads", {}).build()
    source_slack = get_source(token_config, "threads", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)

    # Verify records were returned from the one valid thread
    assert len(output.records) == 2

    # Verify conversations.replies was called exactly once (only for reply_count=3 message)
    replies_calls = [req for req in requests_mock.request_history if "conversations.replies" in req.url]
    assert len(replies_calls) == 1
    assert "channel=airbyte-for-beginners" in replies_calls[0].url
    assert "ts=1577866844.000000" in replies_calls[0].url


def test_channels_stream_with_autojoin(token_config, requests_mock) -> None:
    """
    The test uses the `conversations_list` fixture(autouse=true) as API mocker.
    """
    expected = [
        {"id": "airbyte-for-beginners", "is_member": True, "name": "airbyte-for-beginners"},
        {"id": "good-reads", "is_member": True, "name": "good-reads"},
    ]
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=true",
        json={"channels": expected},
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={"channels": expected},
    )
    state = StateBuilder().with_stream_state("channels", {}).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "channels", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    source_slack = get_source(token_config, "channels", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert [record.record.data for record in output.records] == expected


def test_next_page_token(token_config):
    stream = get_stream_by_name("threads", token_config)
    mocked_response = Mock()
    mocked_response.status_code = 200
    mocked_response.content = b'{"response_metadata": {"next_cursor": "next page"}}'
    mocked_response.headers = {"Content-Type": "application/json"}
    assert get_retriever(stream).paginator.next_page_token(response=mocked_response, last_page_size=100, last_record={"id": "some id"}) == {
        "next_page_token": "next page"
    }


@pytest.mark.parametrize(
    "status_code, response_json, expected",
    (
        pytest.param(200, {"ok": True, "messages": []}, ResponseAction.SUCCESS, id="200_ok_true"),
        pytest.param(403, {}, ResponseAction.FAIL, id="403_fail"),
        pytest.param(429, {}, ResponseAction.RATE_LIMITED, id="429_rate_limited"),
        pytest.param(500, {}, ResponseAction.RETRY, id="500_retry"),
        pytest.param(200, {"ok": False, "error": "ratelimited"}, ResponseAction.RETRY, id="ok_false_ratelimited"),
        pytest.param(200, {"ok": False, "error": "not_in_channel"}, ResponseAction.IGNORE, id="ok_false_not_in_channel"),
        pytest.param(200, {"ok": False, "error": "channel_not_found"}, ResponseAction.IGNORE, id="ok_false_channel_not_found"),
        pytest.param(200, {"ok": False, "error": "is_archived"}, ResponseAction.IGNORE, id="ok_false_is_archived"),
        pytest.param(200, {"ok": False, "error": "request_timeout"}, ResponseAction.RETRY, id="ok_false_request_timeout"),
        pytest.param(200, {"ok": False, "error": "service_unavailable"}, ResponseAction.RETRY, id="ok_false_service_unavailable"),
        pytest.param(200, {"ok": False, "error": "internal_error"}, ResponseAction.RETRY, id="ok_false_internal_error"),
        pytest.param(200, {"ok": False, "error": "missing_scope"}, ResponseAction.FAIL, id="ok_false_auth_error"),
        pytest.param(200, {"ok": False, "error": "token_expired"}, ResponseAction.FAIL, id="ok_false_token_expired"),
        pytest.param(200, {"ok": False, "error": "some_unknown_error"}, ResponseAction.FAIL, id="ok_false_catch_all"),
    ),
)
def test_should_retry(token_config, status_code, response_json, expected):
    stream = get_stream_by_name("threads", token_config)
    mocked_response = MagicMock(spec=Response, status_code=status_code)
    mocked_response.ok = status_code == 200
    mocked_response.headers = {"Content-Type": "application/json"}
    mocked_response.json.return_value = response_json
    assert get_retriever(stream).requester.error_handler.interpret_response(mocked_response).response_action == expected


@pytest.mark.parametrize(
    "slack_error, expected_error_message, expected_failure_type",
    [
        pytest.param(
            "missing_scope",
            "Slack API authentication/permission error: missing_scope.",
            FailureType.config_error,
            id="auth_error_missing_scope",
        ),
        pytest.param(
            "not_authed", "Slack API authentication/permission error: not_authed.", FailureType.config_error, id="auth_error_not_authed"
        ),
        pytest.param(
            "token_revoked",
            "Slack API authentication/permission error: token_revoked.",
            FailureType.config_error,
            id="auth_error_token_revoked",
        ),
        pytest.param(
            "token_expired",
            "Slack API authentication/permission error: token_expired.",
            FailureType.config_error,
            id="auth_error_token_expired",
        ),
        pytest.param("method_not_allowed", "Slack API error: method_not_allowed.", FailureType.system_error, id="general_error_catch_all"),
    ],
)
def test_channels_stream_ok_false_error_handling(requests_mock, token_config, slack_error, expected_error_message, expected_failure_type):
    """
    Verify that Slack API ok=false responses are properly detected as errors
    instead of being silently treated as empty successful results.
    """
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=999&types=public_channel",
        json={"ok": False, "error": slack_error},
    )
    state = StateBuilder().with_stream_state("channels", {}).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "channels", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    source_slack = get_source(token_config, "channels", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert len(output.records) == 0
    assert len(output.errors) > 0
    error_messages = [trace.trace.error.message for trace in output.errors]
    assert any(
        expected_error_message in msg for msg in error_messages
    ), f"Expected error message containing '{expected_error_message}' not found in: {error_messages}"
    assert any(trace.trace.error.failure_type == expected_failure_type for trace in output.errors)


def test_users_stream_ok_false_auth_error(requests_mock, token_config):
    """
    Verify that the users stream properly fails on ok=false auth errors
    instead of returning empty data (silent data loss).
    """
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/users.list?limit=1000",
        json={"ok": False, "error": "invalid_auth"},
    )
    state = StateBuilder().with_stream_state("users", {}).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    source_slack = get_source(token_config, "users", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert len(output.records) == 0
    assert len(output.errors) > 0
    error_messages = [trace.trace.error.message for trace in output.errors]
    assert any("Slack API authentication/permission error: invalid_auth." in msg for msg in error_messages)
    assert any(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)


def test_users_stream_backoff_retry_after_header(requests_mock, token_config):
    """Verify that the users stream honors Slack's Retry-After header on HTTP 429."""
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/users.list",
        [
            {"json": {"error": "ratelimited"}, "headers": {"Retry-After": "1"}, "status_code": 429},
            {"json": {"members": [{"id": "U1", "name": "alice"}]}, "status_code": 200},
        ],
    )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().build()
    source_slack = get_source(token_config, "users", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    retry_logs = [log.log.message for log in output.logs if "Sleeping for 1.0 seconds" in log.log.message]
    assert len(retry_logs) >= 1, "Expected at least one retry with Retry-After for users"
    assert len(output.records) >= 1


def test_channel_members_stream_backoff_retry_after_header(requests_mock, token_config):
    """Verify that the channel_members stream (via base requester) honors Slack's Retry-After header on HTTP 429."""
    # The autouse conversations_list fixture provides channels airbyte-for-beginners and good-reads.
    # Mock conversations.members to return 429 then 200 for the first channel.
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.members?channel=airbyte-for-beginners&limit=1000",
        [
            {"json": {"error": "ratelimited"}, "headers": {"Retry-After": "1"}, "status_code": 429},
            {"json": {"members": ["U1"]}, "status_code": 200},
        ],
    )
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.members?channel=good-reads&limit=1000",
        json={"members": ["U2"]},
    )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "channel_members", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().build()
    source_slack = get_source(token_config, "channel_members", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    retry_logs = [log.log.message for log in output.logs if "Sleeping for 1.0 seconds" in log.log.message]
    assert len(retry_logs) >= 1, "Expected at least one retry with Retry-After for channel_members"
    assert len(output.records) >= 1


def test_channel_messages_stream_ok_false_auth_error(requests_mock, token_config):
    """Verify that channel_messages stream properly fails on ok=false auth errors via the shared $ref handler."""
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history",
        json={"ok": False, "error": "invalid_auth"},
    )
    state = StateBuilder().with_stream_state("channel_messages", {}).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "channel_messages", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    source_slack = get_source(token_config, "channel_messages", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert len(output.records) == 0
    assert len(output.errors) > 0
    error_messages = [trace.trace.error.message for trace in output.errors]
    assert any("Slack API authentication/permission error: invalid_auth." in msg for msg in error_messages)
    assert any(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)


def test_channel_messages_stream_ok_false_not_in_channel(requests_mock, token_config):
    """Verify that channel_messages stream ignores not_in_channel errors instead of failing the sync."""
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.history",
        [
            {"json": {"ok": False, "error": "not_in_channel"}, "status_code": 200},
            {"json": {"ok": True, "messages": [{"ts": "1577866844.000100", "text": "hello"}]}, "status_code": 200},
        ],
    )
    state = StateBuilder().with_stream_state("channel_messages", {}).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "channel_messages", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    source_slack = get_source(token_config, "channel_messages", state)
    output = read(source_slack, config=token_config, catalog=catalog, state=state)
    assert len(output.errors) == 0, f"Expected no errors for IGNORE action, but got: {[t.trace.error.message for t in output.errors]}"


def test_channels_stream_paginator_page_size_is_999(token_config) -> None:
    stream = get_stream_by_name("channels", token_config)
    assert get_retriever(stream).paginator.pagination_strategy.page_size == 999


def test_other_streams_paginator_page_size_is_1000(token_config) -> None:
    for stream_name in ("users", "channel_members", "channel_messages", "threads"):
        stream = get_stream_by_name(stream_name, token_config)
        assert get_retriever(stream).paginator.pagination_strategy.page_size == 1000, f"Expected page_size 1000 for {stream_name}"


def test_channels_stream_with_include_private_channels_false(token_config) -> None:
    stream = get_stream_by_name("channels", token_config)

    params = get_retriever(stream).requester.get_request_params()

    assert params.get("types") == "public_channel"


def test_channels_stream_with_include_private_channels(token_config) -> None:
    config = deepcopy(token_config)
    config["include_private_channels"] = True

    stream = get_stream_by_name("channels", config)

    params = get_retriever(stream).requester.get_request_params()

    assert params.get("types") == "public_channel,private_channel"


def test_channels_stream_excludes_archived_when_explicitly_disabled(token_config) -> None:
    config = deepcopy(token_config)
    config["include_archived_channels"] = False

    stream = get_stream_by_name("channels", config)

    params = get_retriever(stream).requester.get_request_params()

    assert params.get("exclude_archived") == "true"


def test_channels_stream_includes_archived_when_configured(token_config) -> None:
    config = deepcopy(token_config)
    config["include_archived_channels"] = True

    stream = get_stream_by_name("channels", config)

    params = get_retriever(stream).requester.get_request_params()

    assert params.get("exclude_archived") == "false"
