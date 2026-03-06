# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.streams.call_rate import (
    MovingWindowCallRatePolicy,
    UnlimitedCallRatePolicy,
)
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_stream_by_name, oauth_config, token_config


def test_channel_members_extractor(token_config, components_module):
    response_mock = MagicMock()
    members_data = {"members": ["U023BECGF", "U061F7AUR", "W012A3CDE"]}
    response_mock.content = json.dumps(members_data).encode("utf-8")
    records = components_module.ChannelMembersExtractor(config=token_config, parameters={}, field_path=["members"]).extract_records(
        response=response_mock
    )
    assert records == [
        {"member_id": "U023BECGF"},
        {"member_id": "U061F7AUR"},
        {"member_id": "W012A3CDE"},
    ]


def test_join_channels(token_config, requests_mock, joined_channel, components_module):
    mocked_request = requests_mock.post(
        url="https://slack.com/api/conversations.join",
        json={"ok": True, "channel": joined_channel},
    )
    token = token_config["credentials"]["api_token"]
    authenticator = TokenAuthenticator(token)
    channel_filter = token_config["channel_filter"]
    stream = components_module.JoinChannelsStream(authenticator=authenticator, channel_filter=channel_filter)
    records = stream.read_records(
        sync_mode=SyncMode.full_refresh,
        stream_slice={"channel": "C061EG9SL", "channel_name": "general"},
    )
    assert not list(records)
    assert mocked_request.called


def get_channels_retriever_instance(token_config, components_module):
    return components_module.ChannelsRetriever(
        config=token_config,
        requester=HttpRequester(
            name="channels",
            path="conversations.list",
            url_base="https://slack.com/api/",
            config=token_config,
            parameters={},
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
            {
                "ok": True,
                "channel": {
                    "is_member": True,
                    "id": "good-reads",
                    "name": "good-reads",
                },
            },
            "Successfully joined channel: good-reads",
        ),
        (
            {"ok": False, "error": "missing_scope", "needed": "channels:write"},
            "Unable to joined channel: good-reads. Reason: {'ok': False, 'error': 'missing_scope', 'needed': 'channels:write'}",
        ),
    ),
    ids=["successful_join_to_channel", "failed_join_to_channel"],
)
def test_join_channel_read(
    requests_mock,
    token_config,
    joined_channel,
    caplog,
    join_response,
    log_message,
    components_module,
):
    mocked_request = requests_mock.post(url="https://slack.com/api/conversations.join", json=join_response)
    requests_mock.get(
        url="https://slack.com/api/conversations.list",
        json={
            "channels": [
                {
                    "is_member": True,
                    "id": "airbyte-for-beginners",
                    "name": "airbyte-for-beginners",
                },
                {"is_member": False, "id": "good-reads", "name": "good-reads"},
            ]
        },
    )

    retriever = get_channels_retriever_instance(token_config, components_module)
    assert len(list(retriever.read_records(records_schema={}))) == 2
    assert mocked_request.called
    assert mocked_request.last_request._request.body == b'{"channel": "good-reads"}'
    assert log_message in caplog.text


@pytest.mark.parametrize(
    "config_overrides, record, expected",
    (
        # Default: all public channels included
        ({}, {"name": "general", "is_ext_shared": False, "is_private": False}, True),
        # include_public_channels=False: standard public channels excluded
        (
            {"include_public_channels": False},
            {"name": "general", "is_ext_shared": False, "is_private": False},
            False,
        ),
        # include_public_channels=False: external shared channels still included
        (
            {"include_public_channels": False},
            {"name": "ext-acme", "is_ext_shared": True, "is_private": False},
            True,
        ),
        # include_shared_channels=False: external shared channels excluded
        (
            {"include_shared_channels": False},
            {"name": "ext-acme", "is_ext_shared": True, "is_private": False},
            False,
        ),
        # include_shared_channels=False: standard public channels still included
        (
            {"include_shared_channels": False},
            {"name": "general", "is_ext_shared": False, "is_private": False},
            True,
        ),
        # channel_filter whitelist with exact match
        (
            {"channel_filter": ["acme", "globetech"]},
            {"name": "acme", "is_ext_shared": False, "is_private": False},
            True,
        ),
        # channel_filter whitelist no match
        (
            {"channel_filter": ["acme"]},
            {"name": "random", "is_ext_shared": False, "is_private": False},
            False,
        ),
        # channel_filter with wildcard
        (
            {"channel_filter": ["acme-*"]},
            {"name": "acme-sales", "is_ext_shared": False, "is_private": False},
            True,
        ),
        # channel_filter with wildcard no match
        (
            {"channel_filter": ["acme-*"]},
            {"name": "globetech-sales", "is_ext_shared": False, "is_private": False},
            False,
        ),
        # channel_exclude_filter blacklist
        (
            {"channel_exclude_filter": ["random"]},
            {"name": "random", "is_ext_shared": False, "is_private": False},
            False,
        ),
        # channel_exclude_filter with wildcard
        (
            {"channel_exclude_filter": ["ext-*"]},
            {"name": "ext-acme", "is_ext_shared": True, "is_private": False},
            False,
        ),
        # exclude takes precedence over include
        (
            {"channel_filter": ["acme"], "channel_exclude_filter": ["acme"]},
            {"name": "acme", "is_ext_shared": False, "is_private": False},
            False,
        ),
    ),
    ids=[
        "default_public_included",
        "no_public_channels",
        "no_public_channels_but_shared_included",
        "no_shared_channels",
        "no_shared_channels_but_public_included",
        "whitelist_exact_match",
        "whitelist_no_match",
        "wildcard_match",
        "wildcard_no_match",
        "blacklist_exact",
        "blacklist_wildcard",
        "exclude_takes_precedence",
    ],
)
def test_is_channel_included(token_config, components_module, config_overrides, record, expected):
    # Start with empty filters to avoid interference from base config's channel_filter
    config = {
        **token_config,
        "channel_filter": [],
        "channel_exclude_filter": [],
        **config_overrides,
    }
    retriever = get_channels_retriever_instance(token_config, components_module)
    assert retriever.is_channel_included(config, record) is expected


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
                        "partition": {
                            "float_ts": "1683104542.931169",
                            "parent_slice": {
                                "channel": "C04KX3KEZ54",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"float_ts": "1753263869"},
                    },
                    {
                        "partition": {
                            "float_ts": "1683104590.931169",
                            "parent_slice": {
                                "channel": "C04KX3KEZ54",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"float_ts": "1753263870"},
                    },
                    {
                        "partition": {
                            "float_ts": "1683104590.931169",
                            "parent_slice": {
                                "channel": "C04KX3KEZ54",
                                "parent_slice": {},
                            },
                        },
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
    stream = get_stream_by_name(
        "threads",
        token_config,
        StateBuilder().with_stream_state("threads", threads_stream_state).build(),
    )
    assert stream.cursor.state.get("parent_state", {}).get("channel_messages", None) == expected_parent_state


@pytest.mark.parametrize(
    "response_status_code, api_response, config, expected_policy",
    (
        (
            429,
            [
                # first call rate limited
                {
                    "headers": {"Retry-After": "1"},
                    "text": "rate limited",
                    "status_code": 429,
                },
                # refreshed limits on second call
                {"json": {"messages": []}, "status_code": 200},
            ],
            "oauth",
            MovingWindowCallRatePolicy,
        ),
        (
            429,
            [
                # first call rate limited
                {
                    "headers": {"Retry-After": "1"},
                    "text": "rate limited",
                    "status_code": 429,
                },
                # refreshed limits on second call
                {"json": {"messages": []}, "status_code": 200},
            ],
            "token",
            UnlimitedCallRatePolicy,
        ),
        (
            200,
            [
                # no rate limits
                {"json": {"messages": []}, "status_code": 200},
            ],
            "oauth",
            UnlimitedCallRatePolicy,
        ),
    ),
    ids=[
        "rate_limited_oauth_policy",
        "no_rate_limits_token_policy",
        "no_rate_limits_policy",
    ],
)
def tesadfst_threads_and_messages_api_budget(
    response_status_code,
    api_response,
    config,
    expected_policy,
    oauth_config,
    token_config,
    requests_mock,
):
    stream = get_stream_by_name("threads", oauth_config if config == "oauth" else token_config)
    retriever = stream._stream_partition_generator._partition_factory._retriever
    assert len(retriever.requester._http_client._api_budget._policies) == (1 if config == "oauth" else 0)
    if config == "oauth":
        assert isinstance(
            retriever.requester._http_client._api_budget._policies[0],
            UnlimitedCallRatePolicy,
        )

    messages = [{"ts": 1577866844}, {"ts": 1577877406}]

    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.replies",
        api_response,
    )
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

    list(record for partition in stream.generate_partitions() for record in partition.read())

    assert len(retriever.requester._http_client._api_budget._policies) == (1 if config == "oauth" else 0)
    if config == "oauth":
        assert isinstance(retriever.requester._http_client._api_budget._policies[0], expected_policy)
