#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class DiscordMembersStream(HttpStream):
    url_base = "https://discord.com"
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.guild_id = config["guild_id"]
        self.guild_name = config["guild_name"]
        self.job_time = config["job_time"]
        self.server_token = config["server_token"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {"Authorization": "Bot " + self.server_token}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **_) -> MutableMapping[str, Any]:
        if not next_page_token:
            return None
        return next_page_token

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        users = response.json()
        id_array = []
        for user in users:
            user_base = user['user']
            user_base['guild_joined_at'] = user['joined_at']
            user_base['guild_nick'] = user['nick']
            user_base['guild_name'] = self.guild_name
            user_base['guild_id'] = self.guild_id
            user_base['timestamp'] = self.job_time
            id_array.append(user_base)
        return id_array

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()

        # End execution in case the response is empty
        if not decoded_response:
            return None

        # FIND HIGHEST ID
        max_id = max([i["user"]["id"] for i in decoded_response])

        return {"after": max_id}


class Members(DiscordMembersStream):
    def path(self, **_) -> str:
        return f"api/v10/guilds/{self.guild_id}/members?limit=1000"
