#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class DiscordServerPreviewStream(HttpStream):
    url_base = "https://discord.com"
    primary_key = ""

    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.job_time = config["job_time"]
        self.guild_id = config["guild_id"]
        self.server_token = config["server_token"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {"Authorization": "Bot " + self.server_token}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        datas = response.json()
        datas["timestamp"] = self.job_time
        return [datas]
        # yield from [response.json()]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class ServerPreview(DiscordServerPreviewStream):
    def path(self, **_) -> str:
        return f"api/v10/guilds/{self.guild_id}/preview"
