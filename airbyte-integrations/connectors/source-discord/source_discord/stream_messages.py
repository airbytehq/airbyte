#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from .stream_channels import Channels
from requests.exceptions import HTTPError
from airbyte_cdk.sources.streams import Stream
from abc import ABC

SECONDS_BETWEEN_PAGE = 5


class DiscordMessagesStream(HttpStream, ABC):
    url_base = "https://discord.com"
    cursor_field = "timestamp"
    primary_key = "message_id"

    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.config = config
        self.message_limit = 100
        self.max_page_limit = 100
        self.channel_id_current_page_limit = {}
        self.server_token = config["server_token"]
        self.guild_id = config["guild_id"]
        self.job_time = config['job_time']
        self.channel_ids = config['channel_ids'].split(',') if config['channel_ids'] else []
        self._cursor_value = datetime.utcnow()
        self.channels_stream = Channels(
            config=config
        )

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {"Authorization": "Bot " + self.server_token}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        if not next_page_token:
            return {'limit': self.message_limit}

        return {'before': next_page_token['last_message_id'], 'limit': self.message_limit}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        messages = response.json()

        if len(messages) < self.message_limit:
            return None

        channel_id = messages[0]['channel_id']

        if not channel_id in self.channel_id_current_page_limit.keys():
            self.channel_id_current_page_limit[channel_id] = 1
        else:
            self.channel_id_current_page_limit[channel_id] = self.channel_id_current_page_limit[channel_id] + 1

        if self.channel_id_current_page_limit[channel_id] >= self.max_page_limit:
            return None

        print('channel_id_current_page_limit ---->>>>>', self.channel_id_current_page_limit[channel_id])
        return {'last_message_id': messages[-1]['id']}

    def read_records(
            self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(stream_slice=stream_slice, **kwargs)
        except HTTPError as e:
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e


class Messages(DiscordMessagesStream):
    cursor_field = "message_timestamp"

    def read_incremental(self, stream_instance: Stream, stream_state: MutableMapping[str, Any]):
        slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
        for _slice in slices:
            records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=_slice, stream_state=stream_state)
            for record in records:
                yield record

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        url = f"api/v10/channels/{stream_slice['id']}/messages"
        print('message --------------- url path', url)
        return f"api/v10/channels/{stream_slice['id']}/messages"

    def read_records(
            self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        incremental_records = self.read_incremental(self.channels_stream, stream_state=stream_state)
        for incremental_record in incremental_records:
            channel_id = incremental_record['id']
            if channel_id in self.channel_ids:
                stream_slice = {"id": channel_id}
                yield from super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        time.sleep(10)
        for record in records:
            yield self.transform(record=record, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        reaction_count = 0

        if 'reactions' in record.keys():
            reactions = record['reactions']
            for reaction in reactions:
                reaction_count = reaction_count + reaction['count']

        thread = None
        if 'thread' in record.keys():
            thread = record['thread']

        referenced_message = None
        if 'referenced_message' in record.keys():
            if record['referenced_message']:
                referenced_message = record['referenced_message']
        result = {
            'message_id': record['id'],
            'message_type': record['type'],
            'content': record['content'],
            'message_timestamp': record['timestamp'],
            'edited_timestamp': record['edited_timestamp'],
            'timestamp': self.job_time,
            'channel_id': record['channel_id'],
            'guild_id': self.guild_id,
            'author_id': record['author']['id'],
            'author_username': record['author']['username'],
            'referenced_message_id': referenced_message['id'] if referenced_message else None,
            'referenced_message_type': referenced_message['type'] if referenced_message else None,
            'reaction_count': reaction_count,
            'thread_id': thread['id'] if thread else None,
            'thread_parent_id': thread['parent_id'] if thread else None,
            'thread_owner_id': thread['owner_id'] if thread else None,
            'thread_name': thread['name'] if thread else None,
            'thread_message_count': thread['message_count'] if thread else None,
            'thread_message_member_count': thread['member_count'] if thread else None,
            'mention_count': len(record['mentions']),
            'mention_everyone': record['mention_everyone']
        }
        print('message ****** transform ------->>> result', result)
        return result

