#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple
import json
import datetime
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_channels import Channels
from .stream_members import Members
from .stream_messages import Messages
from .stream_roles import Roles
from .stream_server_preview import ServerPreview


class SourceDiscord(AbstractSource):

    def get_guild_name(self, guild_id: str, headers):
        guild_result = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/preview', headers=headers)
        guild_result = json.loads(guild_result.text)
        guild_name = guild_result['name']
        return guild_name

    def check_connection(self, _, config) -> Tuple[bool, str]:

        headers = {"Authorization": f"Bot {config['server_token']}"}

        url = "https://discord.com/api/users/@me"
        response = requests.get(url, headers=headers)
        j_response = response.json()
        if "id" not in j_response:
            return False, "missing id"
        if j_response["id"] != config["bot_id"]:
            return False, "wrong id"
        return True, "accepted"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        headers = {"Authorization": f"Bot {config['server_token']}"}
        guild_name = config['guild_name'] if config['guild_name'] else self.get_guild_name(guild_id=config['guild_id'], headers=headers)

        config['guild_name'] = guild_name
        config["job_time"] = datetime.datetime.now()

        server_preview_stream = ServerPreview(config)
        print('config --- start -----', config)
        channel_stream = Channels(config)
        message_stream = Messages(config)
        member_stream = Members(config)
        role_stream = Roles(config)

        return [
            server_preview_stream,
            channel_stream,
            message_stream,
            member_stream,
            role_stream
        ]
