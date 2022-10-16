#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from pendulum import DateTime, Period


class SlackStream(HttpStream, ABC):
    url_base = "https://slack.com/api/"
    primary_key = "id"
    page_size = 100

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


class ChanneledStream(SlackStream, ABC):
    """Slack stream with channel filter"""

    def __init__(self, channel_filter: List[str] = [], **kwargs):
        self.channel_filter = channel_filter
        super().__init__(**kwargs)


class Channels(ChanneledStream):
    data_field = "channels"

    @property
    def use_cache(self) -> bool:
        return True

    def path(self, **kwargs) -> str:
        return "conversations.list"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["types"] = "public_channel"
        return params

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[MutableMapping]:
        json_response = response.json()
        channels = json_response.get(self.data_field, [])
        if self.channel_filter:
            channels = [channel for channel in channels if channel["name"] in self.channel_filter]
        yield from channels


class ChannelMembers(ChanneledStream):
    data_field = "members"
    primary_key = ["member_id", "channel_id"]

    def path(self, **kwargs) -> str:
        return "conversations.members"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params["channel"] = stream_slice["channel_id"]
        return params

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for member_id in super().parse_response(response, **kwargs):
            # Slack just returns raw IDs as a string, so we want to put them in a "join table" format
            yield {"member_id": member_id, "channel_id": stream_slice["channel_id"]}

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        channels_stream = Channels(authenticator=self._session.auth, channel_filter=self.channel_filter)
        for channel_record in channels_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"channel_id": channel_record["id"]}


class Users(SlackStream):
    data_field = "members"

    def path(self, **kwargs) -> str:
        return "users.list"


# Incremental Streams
def chunk_date_range(start_date: DateTime, interval=pendulum.duration(days=1), end_date: Optional[DateTime] = None) -> Iterable[Period]:
    """
    Yields a list of the beginning and ending timestamps of each day between the start date and now.
    The return value is a pendulum.period
    """

    end_date = end_date or pendulum.now()
    # Each stream_slice contains the beginning and ending timestamp for a 24 hour period
    chunk_start_date = start_date
    while chunk_start_date < end_date:
        chunk_end_date = min(chunk_start_date + interval, end_date)
        yield pendulum.period(chunk_start_date, chunk_end_date)
        chunk_start_date = chunk_end_date


class IncrementalMessageStream(ChanneledStream, ABC):
    data_field = "messages"
    cursor_field = "float_ts"
    primary_key = ["channel_id", "ts"]

    def __init__(self, default_start_date: DateTime, end_date: Optional[DateTime] = None, **kwargs):
        self._start_ts = default_start_date.timestamp()
        self._end_ts = end_date and end_date.timestamp()
        self.set_sub_primary_key()
        super().__init__(**kwargs)

    def set_sub_primary_key(self):
        if isinstance(self.primary_key, list):
            for index, value in enumerate(self.primary_key):
                setattr(self, f"sub_primary_key_{index + 1}", value)
        else:
            logger = AirbyteLogger()
            logger.error("Failed during setting sub primary keys. Primary key should be list.")

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params.update(**stream_slice)
        return params

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            record[self.sub_primary_key_1] = stream_slice.get("channel", "")
            record[self.cursor_field] = float(record[self.sub_primary_key_2])
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        current_stream_state[self.cursor_field] = max(
            latest_record[self.cursor_field], current_stream_state.get(self.cursor_field, self._start_ts)
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
            # this is done to emit at least one state message when no slices are generated
            return []
        return super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)


class ChannelMessages(HttpSubStream, IncrementalMessageStream):
    def path(self, **kwargs) -> str:
        return "conversations.history"

    @property
    def use_cache(self) -> bool:
        return True

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
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

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        The logic for incrementally syncing threads is not very obvious, so buckle up.

        To get all messages in a thread, one must specify the channel and timestamp of the parent (first) message of that thread,
        basically its ID.

        One complication is that threads can be updated at any time in the future. Therefore, if we wanted to comprehensively sync data
        i.e: get every single response in a thread, we'd have to read every message in the slack instance every time we ran a sync,
        because otherwise there is no way to guarantee that a thread deep in the past didn't receive a new message.

        A pragmatic workaround is to say we want threads to be at least N days fresh i.e: look back N days into the past,
        get every message since, and read all of the thread responses. This is essentially the approach we're taking here via slicing:
        create slices from N days into the past and read all messages in threads since then. We could optionally filter out records we have
        already read, but that's omitted to keep the logic simple to reason about.

        Good luck.
        """

        stream_state = stream_state or {}
        channels_stream = Channels(authenticator=self._session.auth, channel_filter=self.channel_filter)

        if self.cursor_field in stream_state:
            # Since new messages can be posted to threads continuously after the parent message has been posted,
            # we get messages from the latest date
            # found in the state minus X days to pick up any new messages in threads.
            # If there is state always use lookback
            messages_start_date = pendulum.from_timestamp(stream_state[self.cursor_field]) - self.messages_lookback_window
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

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Filtering already read records for incremental sync. Copied state value to X after the last sync
        to really 100% make sure no one can edit the state during the run.
        """

        initial_state = copy.deepcopy(stream_state) or {}

        for record in super().read_records(stream_state=stream_state, **kwargs):
            if record.get(self.cursor_field, 0) >= initial_state.get(self.cursor_field, 0):
                yield record


class JoinChannelsStream(HttpStream):
    """
    This class is a special stream which joins channels because the Slack API only returns messages from channels this bot is in.
    Its responses should only be logged for debugging reasons, not read as records.
    """

    url_base = "https://slack.com/api/"
    http_method = "POST"
    primary_key = "id"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        return [{"message": f"Successfully joined channel: {stream_slice['channel_name']}"}]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None  # No pagination

    def path(self, **kwargs) -> str:
        return "conversations.join"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        channels_stream = Channels(authenticator=self._session.auth)
        for channel in channels_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"channel": channel["id"], "channel_name": channel["name"]}

    def request_body_json(self, stream_slice: Mapping = None, **kwargs) -> Optional[Mapping]:
        return {"channel": stream_slice["channel"]}


class SourceSlack(AbstractSource):
    def _get_authenticator(self, config: Mapping[str, Any]):
        # Added to maintain backward compatibility with previous versions
        if "api_token" in config:
            return TokenAuthenticator(config["api_token"])

        credentials = config.get("credentials", {})
        credentials_title = credentials.get("option_title")
        if credentials_title == "Default OAuth2.0 authorization":
            # We can get `refresh_token` only if the token rotation function is enabled for the Slack Oauth Application.
            # If it is disabled, then we use the generated `access_token`, which acts without expiration.
            # https://api.slack.com/authentication/rotation
            if credentials.get("refresh_token", "").strip():
                return Oauth2Authenticator(
                    token_refresh_endpoint="https://slack.com/api/oauth.v2.access",
                    client_id=credentials["client_id"],
                    client_secret=credentials["client_secret"],
                    refresh_token=credentials["refresh_token"],
                )
            return TokenAuthenticator(credentials["access_token"])
        elif credentials_title == "API Token Credentials":
            return TokenAuthenticator(credentials["api_token"])
        else:
            raise Exception(f"No supported option_title: {credentials_title} specified. See spec.json for references")

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            authenticator = self._get_authenticator(config)
            users_stream = Users(authenticator=authenticator)
            next(users_stream.read_records(SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return (
                False,
                f"Got an exception while trying to set up the connection: {e}. "
                f"Most probably, there are no users in the given Slack instance or your token is incorrect",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self._get_authenticator(config)
        default_start_date = pendulum.parse(config["start_date"])
        # this field is not exposed to spec, used only for testing purposes
        end_date = config.get("end_date")
        end_date = end_date and pendulum.parse(end_date)
        threads_lookback_window = pendulum.Duration(days=config["lookback_window"])
        channel_filter = config["channel_filter"]

        channels = Channels(authenticator=authenticator, channel_filter=channel_filter)
        streams = [
            channels,
            ChannelMembers(authenticator=authenticator, channel_filter=channel_filter),
            ChannelMessages(
                parent=channels,
                authenticator=authenticator,
                default_start_date=default_start_date,
                end_date=end_date,
                channel_filter=channel_filter,
            ),
            Threads(
                authenticator=authenticator,
                default_start_date=default_start_date,
                end_date=end_date,
                lookback_window=threads_lookback_window,
                channel_filter=channel_filter,
            ),
            Users(authenticator=authenticator),
        ]

        # To sync data from channels, the bot backed by this token needs to join all those channels. This operation is idempotent.
        if config["join_channels"]:
            logger = AirbyteLogger()
            logger.info("joining Slack channels")
            join_channels_stream = JoinChannelsStream(authenticator=authenticator)
            for stream_slice in join_channels_stream.stream_slices():
                for message in join_channels_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                    logger.info(message["message"])

        return streams
