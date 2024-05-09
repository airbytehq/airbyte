# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from functools import partial
from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers import SinglePartitionRouter
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.streams.core import StreamData
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
        is_ok = response.json().get("ok", False)
        if is_ok:
            self.logger.info(f"Successfully joined channel: {stream_slice['channel_name']}")
        else:
            self.logger.info(f"Unable to joined channel: {stream_slice['channel_name']}. Reason: {response.json()}")
        return []

    def request_body_json(self, stream_slice: Mapping = None, **kwargs) -> Optional[Mapping]:
        if stream_slice:
            return {"channel": stream_slice.get("channel")}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        The pagination is not applicable to this Service Stream.
        """
        return None


class ChannelsRetriever(SimpleRetriever):
    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)
        self.stream_slicer = SinglePartitionRouter(parameters={})
        self.record_selector.transformations = []

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

    def join_channel(self, config: Mapping[str, Any], record: Mapping[str, Any]):
        list(
            self.join_channels_stream(config).read_records(
                sync_mode=SyncMode.full_refresh,
                stream_slice=self.make_join_channel_slice(record),
            )
        )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        _slice = stream_slice or StreamSlice(partition={}, cursor_slice={})  # None-check

        self._paginator.reset()

        most_recent_record_from_slice = None
        record_generator = partial(
            self._parse_records,
            stream_state=self.state or {},
            stream_slice=_slice,
            records_schema=records_schema,
        )

        for stream_data in self._read_pages(record_generator, self.state, _slice):
            # joining channel logic
            if self.should_join_to_channel(self.config, stream_data):
                self.join_channel(self.config, stream_data)

            current_record = self._extract_record(stream_data, _slice)
            if self.cursor and current_record:
                self.cursor.observe(_slice, current_record)

            most_recent_record_from_slice = self._get_most_recent_record(most_recent_record_from_slice, current_record, _slice)
            yield stream_data

        if self.cursor:
            self.cursor.observe(_slice, most_recent_record_from_slice)
        return
