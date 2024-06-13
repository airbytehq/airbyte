#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import CheckpointMixin
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from pendulum import DateTime

from .components.join_channels import JoinChannelsStream
from .utils import chunk_date_range


class SlackStream(HttpStream, ABC):
    url_base = "https://slack.com/api/"
    primary_key = "id"
    page_size = 1000

    @property
    def max_retries(self) -> int:
        # Slack's rate limiting can be unpredictable so we increase the max number of retries by a lot before failing
        return 20

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Slack uses a cursor-based pagination strategy.
        Extract the cursor from the response if it exists and return it in a format
        that can be used to update request parameters"""

        json_response = response.json()
        next_cursor = json_response.get("response_metadata", {}).get("next_cursor")
        if next_cursor:
            return {"cursor": next_cursor}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[MutableMapping]:
        json_response = response.json()
        yield from json_response.get(self.data_field, [])

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """This method is called if we run into the rate limit.
        Slack puts the retry time in the `Retry-After` response header so we
        we return that value. If the response is anything other than a 429 (e.g: 5XX)
        fall back on default retry behavior.
        Rate Limits Docs: https://api.slack.com/docs/rate-limits#web"""

        if "Retry-After" in response.headers:
            return int(response.headers["Retry-After"])
        else:
            self.logger.info("Retry-after header not found. Using default backoff value")
            return 5

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == requests.codes.REQUEST_TIMEOUT or super().should_retry(response)


class ChanneledStream(SlackStream, ABC):
    """Slack stream with channel filter"""

    def __init__(self, channel_filter: List[str] = [], join_channels: bool = False, include_private_channels: bool = False, **kwargs):
        self.channel_filter = channel_filter
        self.join_channels = join_channels
        self.include_private_channels = include_private_channels
        self.kwargs = kwargs
        super().__init__(**kwargs)

    @property
    def join_channels_stream(self) -> JoinChannelsStream:
        return JoinChannelsStream(authenticator=self.kwargs.get("authenticator"), channel_filter=self.channel_filter)

    def should_join_to_channel(self, channel: Mapping[str, Any]) -> bool:
        """
        The `is_member` property indicates whether or not the API Bot is already assigned / joined to the channel.
        https://api.slack.com/types/conversation#booleans
        """
        return self.join_channels and not channel.get("is_member")

    def make_join_channel_slice(self, channel: Mapping[str, Any]) -> Mapping[str, Any]:
        channel_id: str = channel.get("id")
        channel_name: str = channel.get("name")
        self.logger.info(f"Joining Slack Channel: `{channel_name}`")
        return {"channel": channel_id, "channel_name": channel_name}


class Channels(ChanneledStream):
    data_field = "channels"

    @property
    def use_cache(self) -> bool:
        return True

    def path(self, **kwargs) -> str:
        return "conversations.list"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["types"] = "public_channel,private_channel" if self.include_private_channels == True else "public_channel"
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[MutableMapping]:
        json_response = response.json()
        channels = json_response.get(self.data_field, [])
        if self.channel_filter:
            channels = [channel for channel in channels if channel["name"] in self.channel_filter]
        yield from channels

    def read_records(self, sync_mode: SyncMode, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Override the default `read_records` method to provide the `JoinChannelsStream` functionality,
        and be able to read all the channels, not just the ones that already has the API Bot joined.
        """
        for channel in super().read_records(sync_mode=sync_mode):
            # check the channel should be joined before reading
            if self.should_join_to_channel(channel):
                # join the channel before reading it
                yield from self.join_channels_stream.read_records(
                    sync_mode=sync_mode,
                    stream_slice=self.make_join_channel_slice(channel),
                )
            # reading the channel data
            self.logger.info(f"Reading the channel: `{channel.get('name')}`")
            yield channel


# Incremental Streams
class IncrementalMessageStream(CheckpointMixin, ChanneledStream, ABC):
    data_field = "messages"
    cursor_field = "float_ts"
    primary_key = ["channel_id", "ts"]

    @property
    def state(self) -> Mapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def __init__(self, default_start_date: DateTime, end_date: Optional[DateTime] = None, **kwargs):
        self._start_ts = default_start_date.timestamp()
        self._end_ts = end_date and end_date.timestamp()
        self.set_sub_primary_key()
        self._state = None
        super().__init__(**kwargs)

    def set_sub_primary_key(self):
        if isinstance(self.primary_key, list):
            for index, value in enumerate(self.primary_key):
                setattr(self, f"sub_primary_key_{index + 1}", value)
        else:
            self.logger.error("Failed during setting sub primary keys. Primary key should be list.")

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params.update(**stream_slice)
        return params

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            record[self.sub_primary_key_1] = stream_slice.get("channel", "")
            record[self.cursor_field] = float(record[self.sub_primary_key_2])
            yield record

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        current_stream_state[self.cursor_field] = max(
            latest_record[self.cursor_field], float(current_stream_state.get(self.cursor_field, self._start_ts))
        )

        return current_stream_state

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            # return an empty iterator
            # this is done to emit at least one state message when no slices are generated
            return iter([])
        for record in super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state):
            self.state = self._get_updated_state(self.state, record)
            yield record


class ChannelMessages(HttpSubStream, IncrementalMessageStream):
    def path(self, **kwargs) -> str:
        return "conversations.history"

    @property
    def use_cache(self) -> bool:
        return True

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}
        start_date = pendulum.from_timestamp(stream_state.get(self.cursor_field, self._start_ts))
        end_date = self._end_ts and pendulum.from_timestamp(self._end_ts)
        slice_yielded = False
        for parent_slice in super().stream_slices(sync_mode=SyncMode.full_refresh):
            channel = parent_slice["parent"]
            for period in chunk_date_range(start_date=start_date, end_date=end_date):
                yield {"channel": channel["id"], "oldest": period.start.timestamp(), "latest": period.end.timestamp()}
                slice_yielded = True
        if not slice_yielded:
            # yield an empty slice to checkpoint state later
            yield {}


class Threads(IncrementalMessageStream):
    def __init__(self, lookback_window: Mapping[str, int], **kwargs):
        self.messages_lookback_window = lookback_window
        super().__init__(**kwargs)

    def path(self, **kwargs) -> str:
        return "conversations.replies"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        The logic for incrementally syncing threads is not very obvious, so buckle up.

        To get all messages in a thread, one must specify the channel and timestamp of the parent (first) message of that thread,
        basically its ID.

        One complication is that threads can be updated at Any time in the future. Therefore, if we wanted to comprehensively sync data
        i.e: get every single response in a thread, we'd have to read every message in the slack instance every time we ran a sync,
        because otherwise there is no way to guarantee that a thread deep in the past didn't receive a new message.

        A pragmatic workaround is to say we want threads to be at least N days fresh i.e: look back N days into the past,
        get every message since, and read all of the thread responses. This is essentially the approach we're taking here via slicing:
        create slices from N days into the past and read all messages in threads since then. We could optionally filter out records we have
        already read, but that's omitted to keep the logic simple to reason about.

        Good luck.
        """

        stream_state = stream_state or {}
        channels_stream = Channels(
            authenticator=self._session.auth, channel_filter=self.channel_filter, include_private_channels=self.include_private_channels
        )

        if self.cursor_field in stream_state:
            # Since new messages can be posted to threads continuously after the parent message has been posted,
            # we get messages from the latest date
            # found in the state minus X days to pick up any new messages in threads.
            # If there is state always use lookback
            messages_start_date = pendulum.from_timestamp(float(stream_state[self.cursor_field])) - self.messages_lookback_window
        else:
            # If there is no state i.e: this is the first sync then there is no use for lookback, just get messages
            # from the default start date
            messages_start_date = pendulum.from_timestamp(self._start_ts)

        messages_stream = ChannelMessages(
            parent=channels_stream,
            authenticator=self._session.auth,
            default_start_date=messages_start_date,
            end_date=self._end_ts and pendulum.from_timestamp(self._end_ts),
        )

        slice_yielded = False
        for message_chunk in messages_stream.stream_slices(stream_state={self.cursor_field: messages_start_date.timestamp()}):
            self.logger.info(f"Syncing replies {message_chunk}")
            for message in messages_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=message_chunk):
                yield {"channel": message_chunk["channel"], self.sub_primary_key_2: message[self.sub_primary_key_2]}
                slice_yielded = True
        if not slice_yielded:
            # yield an empty slice to checkpoint state later
            yield {}
