# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock

import pytest
from requests import Response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_retriever, get_stream_by_name, oauth_config, token_config


def test_channel_members_extractor(token_config, components_module):
    response_mock = MagicMock()
    members_data = {"members": ["U023BECGF", "U061F7AUR", "W012A3CDE"]}
    response_mock.content = json.dumps(members_data).encode("utf-8")
    records = components_module.ChannelMembersExtractor(config=token_config, parameters={}, field_path=["members"]).extract_records(
        response=response_mock
    )
    assert records == [{"member_id": "U023BECGF"}, {"member_id": "U061F7AUR"}, {"member_id": "W012A3CDE"}]


def test_join_channels(token_config, requests_mock, joined_channel, components_module):
    mocked_request = requests_mock.post(url="https://slack.com/api/conversations.join", json={"ok": True, "channel": joined_channel})
    token = token_config["credentials"]["api_token"]
    authenticator = TokenAuthenticator(token)
    channel_filter = token_config["channel_filter"]
    stream = components_module.JoinChannelsStream(authenticator=authenticator, channel_filter=channel_filter)
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"channel": "C061EG9SL", "channel_name": "general"})
    assert not list(records)
    assert mocked_request.called


def get_channels_retriever_instance(token_config, components_module):
    return components_module.ChannelsRetriever(
        config=token_config,
        requester=HttpRequester(
            name="channels", path="conversations.list", url_base="https://slack.com/api/", config=token_config, parameters={}
        ),
        record_selector=RecordSelector(
            extractor=DpathExtractor(field_path=["channels"], config=token_config, parameters={}),
            config=token_config,
            parameters={},
            schema_normalization=None,
        ),
        parameters={},
    )


def test_join_channels_should_join_to_channel(token_config, components_module):
    retriever = get_channels_retriever_instance(token_config, components_module)
    assert retriever.should_join_to_channel(token_config, {"is_member": False}) is True
    assert retriever.should_join_to_channel(token_config, {"is_member": True}) is False


def test_join_channels_make_join_channel_slice(token_config, components_module):
    retriever = get_channels_retriever_instance(token_config, components_module)
    expected_slice = {"channel": "C061EG9SL", "channel_name": "general"}
    assert retriever.make_join_channel_slice({"id": "C061EG9SL", "name": "general"}) == expected_slice


@pytest.mark.parametrize(
    "join_response, log_message",
    (
        (
            {"ok": True, "channel": {"is_member": True, "id": "channel 2", "name": "test channel"}},
            "Successfully joined channel: test channel",
        ),
        (
            {"ok": False, "error": "missing_scope", "needed": "channels:write"},
            "Unable to joined channel: test channel. Reason: {'ok': False, 'error': " "'missing_scope', 'needed': 'channels:write'}",
        ),
    ),
    ids=["successful_join_to_channel", "failed_join_to_channel"],
)
def test_join_channel_read(requests_mock, token_config, joined_channel, caplog, join_response, log_message, components_module):
    mocked_request = requests_mock.post(url="https://slack.com/api/conversations.join", json=join_response)
    requests_mock.get(
        url="https://slack.com/api/conversations.list",
        json={"channels": [{"is_member": True, "id": "channel 1"}, {"is_member": False, "id": "channel 2", "name": "test channel"}]},
    )

    retriever = get_channels_retriever_instance(token_config, components_module)
    assert len(list(retriever.read_records(records_schema={}))) == 2
    assert mocked_request.called
    assert mocked_request.last_request._request.body == b'{"channel": "channel 2"}'
    assert log_message in caplog.text


@pytest.mark.parametrize(
    "threads_stream_state, expected_parent_state",
    (
        ({}, None),
        (
            {"float_ts": 7270247822.0},
            # lookback window applied
            {"float_ts": 7270161422.0},
        ),
        (
            {
                "states": [
                    {
                        "partition": {"float_ts": "1683104542.931169", "parent_slice": {"channel": "C04KX3KEZ54", "parent_slice": {}}},
                        "cursor": {"float_ts": "1753263869"},
                    },
                    {
                        "partition": {"float_ts": "1683104590.931169", "parent_slice": {"channel": "C04KX3KEZ54", "parent_slice": {}}},
                        "cursor": {"float_ts": "1753263870"},
                    },
                    {
                        "partition": {"float_ts": "1683104590.931169", "parent_slice": {"channel": "C04KX3KEZ54", "parent_slice": {}}},
                        "cursor": {"float_ts": "1753263849"},
                    },
                ]
            },
            # lookback window applied
            {"float_ts": 1753177470.0},
        ),
    ),
    ids=["no_state", "old_format_state", "new_format_state"],
)
def test_threads_state_migration(token_config, threads_stream_state, expected_parent_state):
    stream = get_stream_by_name("threads", token_config, StateBuilder().with_stream_state("threads", threads_stream_state).build())
    assert stream.cursor.state.get("parent_state", {}).get("channel_messages", None) == expected_parent_state


@pytest.mark.parametrize(
    "stream_name",
    (
        "threads",
        "channel_messages",
        "users",
        "channel_members",
    ),
)
def test_http_429_returns_rate_limited_action(token_config, stream_name):
    """
    Verify that HTTP 429 responses are mapped to RATE_LIMITED (not RETRY) for all streams.
    RATE_LIMITED raises RateLimitBackoffException which retries indefinitely with backoff,
    while RETRY raises DefaultBackoffException which fails permanently after limited retries.
    This is the fix for https://github.com/airbytehq/oncall/issues/11816.
    """
    stream = get_stream_by_name(stream_name, token_config)
    mocked_response = MagicMock(spec=Response, status_code=429)
    mocked_response.ok = False
    mocked_response.headers = {"Content-Type": "application/json"}
    error_resolution = get_retriever(stream).requester.error_handler.interpret_response(mocked_response)
    assert error_resolution.response_action == ResponseAction.RATE_LIMITED


def test_channel_messages_uses_standard_requester(token_config):
    """
    Verify that channel_messages stream uses the standard HttpRequester (not the removed
    MessagesAndThreadsHttpRequester custom class) and inherits the base error handler
    with RATE_LIMITED action for 429 responses.
    """
    stream = get_stream_by_name("channel_messages", token_config)
    retriever = get_retriever(stream)
    requester = retriever.requester
    # Should be a standard HttpRequester, not a custom subclass
    assert type(requester).__name__ == "HttpRequester"


def test_threads_uses_standard_requester(token_config):
    """
    Verify that threads stream uses the standard HttpRequester (not the removed
    MessagesAndThreadsHttpRequester custom class) and inherits the base error handler
    with RATE_LIMITED action for 429 responses.
    """
    stream = get_stream_by_name("threads", token_config)
    retriever = get_retriever(stream)
    requester = retriever.requester
    # Should be a standard HttpRequester, not a custom subclass
    assert type(requester).__name__ == "HttpRequester"
