# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

LOGGER = logging.getLogger("airbyte_logger")


class JoinChannelsStream(HttpStream):
    """
    This class is a special stream which joins channels because the Slack API only returns messages from channels this bot is in.
    Its responses should only be logged for debugging reasons, not read as records.
    """

    url_base = "https://slack.com/api/"
    http_method = "POST"
    primary_key = "id"

    def __init__(self, channel_filter: List[str] = None, **kwargs):
        self.channel_filter = channel_filter or []
        super().__init__(**kwargs)

    def path(self, **kwargs) -> str:
        return "conversations.join"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable:
        """
        Override to simply indicate that the specific channel was joined successfully.
        This method should not return any data, but should return an empty iterable.
        """
        self.logger.info(f"Successfully joined channel: {stream_slice['channel_name']}")
        yield response.json()["channel"]

    def request_body_json(self, stream_slice: Mapping = None, **kwargs) -> Optional[Mapping]:
        return {"channel": stream_slice["channel"]}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        The pagination is not applicable to this Service Stream.
        """
        return None


@dataclass
class JoinChannels(RecordTransformation):
    """
    Make 'conversations.join' POST request for every found channel id
    if we are not still a member of such channel
    """

    def should_join_to_channel(self, config: Mapping[str, Any], record: Record) -> bool:
        """
        The `is_member` property indicates whether the API Bot is already assigned / joined to the channel.
        https://api.slack.com/types/conversation#booleans
        """
        return config["join_channels"] and not record.get("is_member")

    def make_join_channel_slice(self, channel: Mapping[str, Any]) -> Mapping[str, Any]:
        channel_id: str = channel.get("id")
        channel_name: str = channel.get("name")
        LOGGER.info(f"Joining Slack Channel: `{channel_name}`")
        return {"channel": channel_id, "channel_name": channel_name}

    def join_channels_stream(self, config) -> JoinChannelsStream:
        token = config["credentials"].get("api_token") or config["credentials"].get("access_token")
        authenticator = TokenAuthenticator(token)
        channel_filter = config["channel_filter"]
        return JoinChannelsStream(authenticator=authenticator, channel_filter=channel_filter)

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        if self.should_join_to_channel(config, record):
            channel = list(
                self.join_channels_stream(config).read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_slice=self.make_join_channel_slice(record),
                )
            )
            return channel[0]
        return record
