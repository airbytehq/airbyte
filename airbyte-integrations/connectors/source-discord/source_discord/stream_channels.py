#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping
from abc import ABC
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from typing import Iterable, Optional
from requests.exceptions import HTTPError


class DiscordChannelsStream(HttpStream, ABC):
    url_base = "https://discord.com"
    primary_key = ""

    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.job_time = config["job_time"]
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {"Authorization": "Bot " + self.server_token}

    def read_records(
            self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        for record in records:
            yield self.transform(record=record, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return {
                'id': record['id'],
                'type': record['type'],
                'name': record['name'],
                'guild_id': record['guild_id']
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class Channels(DiscordChannelsStream):
    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"api/v10/guilds/{self.guild_id}/channels"
