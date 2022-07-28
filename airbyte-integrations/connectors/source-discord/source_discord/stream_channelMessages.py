import time
import requests
from datetime import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin

SECONDS_BETWEEN_PAGE = 5


class DiscordMessagesStream(HttpStream, IncrementalMixin):
    url_base = "https://discord.com"
    cursor_field = "timestamp"
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], initial_timestamp: str, **kwargs):
        super().__init__()
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]
        self.channel_id = config["channel_id"]
        self.initial_timestamp = string_to_timestamp(initial_timestamp)
        self._cursor_value = None
        self.latest_stream_timestamp = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.start_date}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = string_to_timestamp(value[self.cursor_field])

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {'Authorization': "Bot " + self.server_token}

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **_) -> MutableMapping[str, Any]:
        if not next_page_token:
            return None
        return next_page_token

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        decoded_response = response.json()

        if not decoded_response:
            return None

        latest_timestamp = string_to_timestamp(decoded_response[-1]["timestamp"])

        if latest_timestamp < self.latest_stream_timestamp:
            return None

        most_recent_id = decoded_response[-1]["id"]
        time.sleep(SECONDS_BETWEEN_PAGE)
        return {"before": most_recent_id}

    def read_records(self, stream_state: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping[str, Any]]:

        if stream_state:
            state_timestamp = string_to_timestamp(stream_state["timestamp"])
        else:
            state_timestamp = self.initial_timestamp

        self.latest_stream_timestamp = state_timestamp

        for record in super().read_records(*args, **kwargs):
            raw_latest_timestamp = record["timestamp"]
            latest_timestamp = string_to_timestamp(raw_latest_timestamp)
            if latest_timestamp <= state_timestamp:
                return
            if self._cursor_value is None:
                self._cursor_value = latest_timestamp
            self._cursor_value = max(self._cursor_value, latest_timestamp)
            yield record


class ChannelMessages(DiscordMessagesStream):
    def path(self, **_) -> str:
        return "api/channels/{}/messages?limit=100".format(self.channel_id)

# Discord returns data with different time formats,
# so there is need to "normalize" it
def string_to_timestamp(text_timestamp: str) -> datetime:
    clean_text_timestamp = text_timestamp[0:19]
    return datetime.strptime(
        clean_text_timestamp,
        "%Y-%m-%dT%H:%M:%S"
    )
