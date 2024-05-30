# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pendulum
import pytest
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode
from source_slack import SourceSlack
from source_slack.components.channel_members_extractor import ChannelMembersExtractor
from source_slack.components.join_channels import ChannelsRetriever, JoinChannelsStream


def get_stream_by_name(stream_name, config):
    streams = SourceSlack().streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def test_channel_members_extractor(token_config):
    response_mock = MagicMock()
    response_mock.json.return_value = {"members": [
        "U023BECGF",
        "U061F7AUR",
        "W012A3CDE"
    ]}
    records = ChannelMembersExtractor(config=token_config, parameters={}, field_path=["members"]).extract_records(response=response_mock)
    assert records == [{"member_id": "U023BECGF"},
                       {"member_id": "U061F7AUR"},
                       {"member_id": "W012A3CDE"}]


def test_join_channels(token_config, requests_mock, joined_channel):
    mocked_request = requests_mock.post(
        url="https://slack.com/api/conversations.join",
        json={"ok": True, "channel": joined_channel}
    )
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
        requester=HttpRequester(name="channels", path="conversations.list", url_base="https://slack.com/api/", config=token_config,
                                parameters={}),
        record_selector=RecordSelector(
            extractor=DpathExtractor(field_path=["channels"], config=token_config, parameters={}),
            config=token_config, parameters={},
            schema_normalization=None),
        parameters={}
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
        ({"ok": True, "channel": {"is_member": True, "id": "channel 2", "name": "test channel"}}, "Successfully joined channel: test channel"),
        ({"ok": False, "error": "missing_scope", "needed": "channels:write"},
         "Unable to joined channel: test channel. Reason: {'ok': False, 'error': " "'missing_scope', 'needed': 'channels:write'}"),
    ),
    ids=["successful_join_to_channel", "failed_join_to_channel"]
)
def test_join_channel_read(requests_mock, token_config, joined_channel, caplog, join_response, log_message):
    mocked_request = requests_mock.post(
        url="https://slack.com/api/conversations.join",
        json=join_response
    )
    requests_mock.get(
        url="https://slack.com/api/conversations.list",
        json={"channels": [{"is_member": True, "id": "channel 1"}, {"is_member": False, "id": "channel 2", "name": "test channel"}]}
    )

    retriever = get_channels_retriever_instance(token_config)
    assert len(list(retriever.read_records(records_schema={}))) == 2
    assert mocked_request.called
    assert mocked_request.last_request._request.body == b'{"channel": "channel 2"}'
    assert log_message in caplog.text
