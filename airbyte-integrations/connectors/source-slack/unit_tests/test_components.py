# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pendulum
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode
from freezegun import freeze_time
from source_slack import SourceSlack
from source_slack.components.channel_members_extractor import ChannelMembersExtractor
from source_slack.components.join_channels import JoinChannels, JoinChannelsStream
from source_slack.components.threads_partition_router import ThreadsPartitionRouter


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
    records = ChannelMembersExtractor(config=token_config, parameters={}, field_path=['members']).extract_records(response=response_mock)
    assert records == [{'member_id': 'U023BECGF'},
                       {'member_id': 'U061F7AUR'},
                       {'member_id': 'W012A3CDE'}]


@freeze_time("2024-03-10T20:00:00Z", tz_offset=-2)
def test_threads_partition_router(token_config, requests_mock):
    start_date = "2024-03-01T20:00:00Z"
    end_date = pendulum.now()
    oldest, latest = int(pendulum.parse(start_date).timestamp()), int(end_date.timestamp())
    token_config["start_date"] = start_date
    for channel in token_config["channel_filter"]:
        requests_mock.get(
            url=f"https://slack.com/api/conversations.history?"
                f"inclusive=True&limit=1000&channel={channel}&"
                f"oldest={oldest}&latest={latest}",
            json={"messages": [{"ts": latest}, {"ts": oldest}]}
        )

    channel_messages_stream = get_stream_by_name("channel_messages", token_config)
    router = ThreadsPartitionRouter(
        config=token_config,
        parameters={},
        parent_stream_configs=[
            ParentStreamConfig(
                config=token_config,
                stream=channel_messages_stream,
                parent_key="ts",
                partition_field="ts",
                parameters={},
                request_option=RequestOption(field_name="ts", inject_into="request_parameter", parameters={})
            ), ]
    )
    slices = router.stream_slices()
    expected = [{"channel": "airbyte-for-beginners", "ts": latest},
                {"channel": "airbyte-for-beginners", "ts": oldest},
                {"channel": "good-reads", "ts": latest},
                {"channel": "good-reads", "ts": oldest}]

    assert list(slices) == expected


def test_join_channels(token_config, requests_mock, joined_channel):
    requests_mock.post(
        url="https://slack.com/api/conversations.join",
        json={"channel": joined_channel}
    )
    token = token_config["credentials"]["api_token"]
    authenticator = TokenAuthenticator(token)
    channel_filter = token_config["channel_filter"]
    stream = JoinChannelsStream(authenticator=authenticator, channel_filter=channel_filter)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"channel": "C061EG9SL", "channel_name": "general"}))
    assert records[0] == joined_channel


def test_join_channels_should_join_to_channel(token_config):
    transformation = JoinChannels()
    assert transformation.should_join_to_channel(token_config, {"is_member": False}) is True
    assert transformation.should_join_to_channel(token_config, {"is_member": True}) is False


def test_join_channels_make_join_channel_slice(token_config):
    transformation = JoinChannels()
    assert transformation.make_join_channel_slice({"id": "C061EG9SL", "name": "general"}) == {"channel": "C061EG9SL",
                                                                                              "channel_name": "general"}


def test_join_channel_transformation(requests_mock, token_config, joined_channel):
    requests_mock.post(
        url="https://slack.com/api/conversations.join",
        json={"channel": joined_channel}
    )

    transformation = JoinChannels()
    assert transformation.transform(config=token_config, record={"is_member": True}) == {"is_member": True}
    assert transformation.transform(config=token_config, record={"is_member": False}) == joined_channel
