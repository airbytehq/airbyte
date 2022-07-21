from __future__ import annotations
import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import AirbyteConnectionStatus
from airbyte_cdk.models import Status
from airbyte_cdk.sources.streams.http import HttpStream


class SourceDiscord(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        # TODO
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [ServerPreview(config)]


class DiscordStream(HttpStream):
    url_base = "https://discord.com"
    primary_key = None

    guild_id = ""
    server_token = ""
    
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {'Authorization': "Bot " + self.server_token}

    def parse_response(
        self,
        response: requests.Response,
        **kwargs
    ) -> Iterable[Mapping]:
        yield from [response.json()]

    def next_page_token(
        self,
        response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        return None


class ServerPreview(DiscordStream):
    def path(self, **kwargs) -> str:
        return "api/guilds/{}/preview".format(self.guild_id)
