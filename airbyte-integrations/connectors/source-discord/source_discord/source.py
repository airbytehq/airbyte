from math import nextafter
from operator import ne
from pendulum import time
import requests
from datetime import datetime, timedelta
from typing import Any, Mapping, Tuple, List, Iterable, Optional, MutableMapping, Union
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin

timestamp_format = "%Y-%m-%dT%H:%M:%S.%f+00:00"

class SourceDiscord(AbstractSource):

    # Check discord api response with a local env variable
    def check_connection(self, _, config) -> Tuple[bool, Any]:
        url = "https://discord.com/api/users/@me"
        headers = {"Authorization": "Bot {}".format(config["server_token"])}
        response = requests.get(url, headers=headers)
        j_response = response.json()
        if j_response["id"] != config["bot_id"]:
            return False, None
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        initial_timestamp = datetime.strptime(config["initial_timestamp"], timestamp_format)
        return [
            ServerPreview(config),
            ChannelMessages(config, initial_timestamp=initial_timestamp)
        ]


class DiscordBasicStream(HttpStream):
    url_base = "https://discord.com"
    primary_key = ""
    
    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {'Authorization': "Bot " + self.server_token}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        yield from [response.json()]

    def next_page_token(self, _) -> Optional[Mapping[str, Any]]:
        return None


class DiscordMessagesStream(HttpStream, IncrementalMixin):
    url_base = "https://discord.com"
    cursor_field = "timestamp"
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], initial_timestamp: datetime, **kwargs):
        super().__init__()
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]
        self.channel_id = config["channel_id"]
        self.initial_timestamp = initial_timestamp
        self._cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime(timestamp_format)}
        else:
            return {self.cursor_field: self.start_date.strftime(timestamp_format)}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], timestamp_format)

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

        latest_timestamp = datetime.strptime(decoded_response[-1]["timestamp"], timestamp_format)
        if latest_timestamp < self._cursor_value:
            return None

        most_recent_id = decoded_response[-1]["id"]
        return {"before": most_recent_id}

    def read_records(self, stream_state: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping[str, Any]]:

        if stream_state:
            state_timestamp = datetime.strptime(stream_state["timestamp"], timestamp_format)
        else:
            state_timestamp = self.initial_timestamp

        for record in super().read_records(*args, **kwargs):
            print("\n")
            raw_latest_timestamp = record["timestamp"]
            latest_timestamp = datetime.strptime(raw_latest_timestamp, timestamp_format)
            if latest_timestamp <= state_timestamp:
                return
            if self._cursor_value is None:
                self._cursor_value = latest_timestamp
            self._cursor_value = max(self._cursor_value, latest_timestamp)
            yield record


class ServerPreview(DiscordBasicStream):
    def path(self, **_) -> str:
        return "api/guilds/{}/preview".format(self.guild_id)


class ChannelMessages(DiscordMessagesStream):
    def path(self, **_) -> str:
        return "api/channels/{}/messages".format(self.channel_id)