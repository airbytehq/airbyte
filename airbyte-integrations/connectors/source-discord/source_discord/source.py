import requests
from typing import Any, Mapping, Tuple, List, Iterable, Optional
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class SourceDiscord(AbstractSource):

    # Check discord api response with a local env varible
    def check_connection(self, _, config) -> Tuple[bool, Any]:
        url = "https://discord.com/api/users/@me"
        headers = {"Authorization": "Bot {}".format(config["server_token"])}
        response = requests.get(url, headers=headers)
        j_response = response.json()
        if j_response["id"] != config["bot_id"]:
            return False, None
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [ServerPreview(config)]


class DiscordStream(HttpStream):
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


class ServerPreview(DiscordStream):
    def path(self, **_) -> str:
        return "api/guilds/{}/preview".format(self.guild_id)
