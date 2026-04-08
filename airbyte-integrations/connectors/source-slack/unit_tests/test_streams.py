#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from unittest.mock import MagicMock, Mock

import pytest
from requests import Response

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, SyncMode
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
        "https://slack.com/api/conversations.list?limit=1000&types=public_channel",
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
    "status_code, expected",
    (
        (200, ResponseAction.SUCCESS),
        (403, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
    ),
)
def test_should_retry(token_config, status_code, expected):
    stream = get_stream_by_name("threads", token_config)
    mocked_response = MagicMock(spec=Response, status_code=status_code)
    mocked_response.ok = status_code == 200
    mocked_response.headers = {"Content-Type": "application/json"}
    assert get_retriever(stream).requester.error_handler.interpret_response(mocked_response).response_action == expected


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
