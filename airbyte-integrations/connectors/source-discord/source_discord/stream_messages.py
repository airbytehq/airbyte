import time
import requests
from datetime import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin

from .stream_channels import Channels

SECONDS_BETWEEN_PAGE = 5


class DiscordMessagesStream(HttpStream, IncrementalMixin):
    url_base = "https://discord.com"
    cursor_field = "timestamp"
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], initial_timestamp: str, **kwargs):
        super().__init__()
        self.config = config
        self.server_token = config["server_token"]
        self.channel_ids = config["channel_ids"]
        self._cursor_value = datetime.utcnow()
        self.latest_stream_timestamp = string_to_timestamp(initial_timestamp)

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {'Authorization': "Bot " + self.server_token}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **_) -> MutableMapping[str, Any]:
        if not next_page_token:
            return None
        return next_page_token

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        decoded_response = response.json()

        # End execution in case the response is empty
        if not decoded_response:
            return None

        # End execution in case a message is already processed
        latest_timestamp = string_to_timestamp(decoded_response[-1]["timestamp"])
        if latest_timestamp < self.latest_stream_timestamp:
            return None

        time.sleep(SECONDS_BETWEEN_PAGE)
        most_recent_id = decoded_response[-1]["id"]
        return {"before": most_recent_id}

    def read_records(self, stream_state: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping[str, Any]]:

        if stream_state:
            self.latest_stream_timestamp = string_to_timestamp(stream_state["timestamp"])

        for record in super().read_records(*args, **kwargs):
            record_timestamp = string_to_timestamp(record["timestamp"])
            # End execution in case a message is already processed
            if record_timestamp <= self.latest_stream_timestamp:
                return
            yield record
    
    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.utcnow()


class Messages(DiscordMessagesStream):

    def stream_slices(self, **kwargs):
        channels_stream = Channels(self.config)
        for channel in channels_stream.read_records(sync_mode=SyncMode.full_refresh):
            if channel["id"] in self.channel_ids.split(","):
                yield {"channel_id": channel["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        channel_id = stream_slice["channel_id"]
        return f"api/channels/{channel_id}/messages?limit=100"

# Discord returns data with different time formats,
# so there is need to "normalize" it
def string_to_timestamp(text_timestamp: str) -> datetime:
    clean_text_timestamp = text_timestamp[0:19]
    return datetime.strptime(
        clean_text_timestamp,
        "%Y-%m-%dT%H:%M:%S"
    )
