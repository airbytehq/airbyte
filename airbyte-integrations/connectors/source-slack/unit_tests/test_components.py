# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock

import pytest
from source_slack import SourceSlack
from source_slack.components.channel_members_extractor import ChannelMembersExtractor
from source_slack.components.join_channels import ChannelsRetriever, JoinChannelsStream
from source_slack.components.threads_partition_router import ThreadsPartitionRouter

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.streams.call_rate import MovingWindowCallRatePolicy, UnlimitedCallRatePolicy
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from unit_tests.conftest import oauth_config, token_config


def get_stream_by_name(stream_name, config):
    streams = SourceSlack(catalog={}, config=config, state={}).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def test_channel_members_extractor(token_config):
    response_mock = MagicMock()
    members_data = {"members": ["U023BECGF", "U061F7AUR", "W012A3CDE"]}
    response_mock.content = json.dumps(members_data).encode("utf-8")
    records = ChannelMembersExtractor(config=token_config, parameters={}, field_path=["members"]).extract_records(response=response_mock)
    assert records == [{"member_id": "U023BECGF"}, {"member_id": "U061F7AUR"}, {"member_id": "W012A3CDE"}]


def test_join_channels(token_config, requests_mock, joined_channel):
    mocked_request = requests_mock.post(url="https://slack.com/api/conversations.join", json={"ok": True, "channel": joined_channel})
    token = token_config["credentials"]["api_token"]
    authenticator = TokenAuthenticator(token)
    channel_filter = token_config["channel_filter"]
    stream = JoinChannelsStream(authenticator=authenticator, channel_filter=channel_filter)
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"channel": "C061EG9SL", "channel_name": "general"})
    assert not list(records)
    assert mocked_request.called


def get_channels_retriever_instance(token_config):
    return ChannelsRetriever(
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


def test_join_channels_should_join_to_channel(token_config):
    retriever = get_channels_retriever_instance(token_config)
    assert retriever.should_join_to_channel(token_config, {"is_member": False}) is True
    assert retriever.should_join_to_channel(token_config, {"is_member": True}) is False


def test_join_channels_make_join_channel_slice(token_config):
    retriever = get_channels_retriever_instance(token_config)
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
def test_join_channel_read(requests_mock, token_config, joined_channel, caplog, join_response, log_message):
    mocked_request = requests_mock.post(url="https://slack.com/api/conversations.join", json=join_response)
    requests_mock.get(
        url="https://slack.com/api/conversations.list",
        json={"channels": [{"is_member": True, "id": "channel 1"}, {"is_member": False, "id": "channel 2", "name": "test channel"}]},
    )

    retriever = get_channels_retriever_instance(token_config)
    assert len(list(retriever.read_records(records_schema={}))) == 2
    assert mocked_request.called
    assert mocked_request.last_request._request.body == b'{"channel": "channel 2"}'
    assert log_message in caplog.text


@pytest.mark.parametrize(
    "threads_stream_state, expected_parent_state",
    (
        ({}, {}),
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
def test_threads_partition_router(token_config, threads_stream_state, expected_parent_state):
    stream = get_stream_by_name("threads", token_config)
    threads_partition_router = stream.retriever.stream_slicer._partition_router
    threads_partition_router.set_initial_state(stream_state=threads_stream_state)
    assert threads_partition_router.parent_stream_configs[0].stream.state["state"] == expected_parent_state


@pytest.mark.parametrize(
    "response_status_code, api_response, config, expected_policy",
    (
        (
            429,
            [
                # first call rate limited
                {"headers": {"Retry-After": "1"}, "text": "rate limited", "status_code": 429},
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
                {"headers": {"Retry-After": "1"}, "text": "rate limited", "status_code": 429},
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
    ids=["rate_limited_oauth_policy", "no_rate_limits_token_policy", "no_rate_limits_policy"],
)
def test_threads_and_messages_api_budget(
    response_status_code, api_response, config, expected_policy, oauth_config, token_config, requests_mock
):
    stream = get_stream_by_name("threads", oauth_config if config == "oauth" else token_config)
    assert len(stream.retriever.requester._http_client._api_budget._policies) == (1 if config == "oauth" else 0)
    if config == "oauth":
        assert isinstance(stream.retriever.requester._http_client._api_budget._policies[0], UnlimitedCallRatePolicy)

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

    stream_slice = list(stream.stream_slices(sync_mode=SyncMode.incremental, stream_state={}))[0]

    list(stream.retriever.read_records(records_schema={}, stream_slice=stream_slice))

    assert len(stream.retriever.requester._http_client._api_budget._policies) == (1 if config == "oauth" else 0)
    if config == "oauth":
        assert isinstance(stream.retriever.requester._http_client._api_budget._policies[0], expected_policy)
