from math import nextafter
import requests
from typing import Any, Mapping, Tuple, List, Iterable, Optional, MutableMapping
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


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
        return [
            ServerPreview(config),
            ChannelMessages(config)
        ]


class DiscordBasicStream(HttpStream):
    url_base = "https://discord.com" # pyright: ignore
    primary_key = "" # pyright: ignore
    
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


class DiscordMessagesStream(HttpStream):
    url_base = "https://discord.com" # pyright: ignore
    primary_key = "id" # pyright: ignore

    cursor_field = "timestamp" # pyright: ignore

    counter = 0 # TO BE REMOVED
    
    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]
        self.channel_id = config["channel_id"]
        self._cursor_value = None

        self.counter = 0 # TO BE REMOVED

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {'Authorization': "Bot " + self.server_token}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **_) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        return next_page_token

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        self.counter = self.counter + 1 # TO BE REMOVED

        decoded_response = response.json()
        last_object_id = decoded_response[-1]["id"]
        print("\n\n", last_object_id, "\n\n")
        if self.counter > 2: # TO BE REMOVED
            return None
        return {"before", last_object_id}

class ServerPreview(DiscordBasicStream):
    def path(self, **_) -> str:
        return "api/guilds/{}/preview".format(self.guild_id)


class ChannelMessages(DiscordMessagesStream):
    def path(self, **_) -> str:
        return "api/channels/{}/messages?limit=3".format(self.channel_id)
