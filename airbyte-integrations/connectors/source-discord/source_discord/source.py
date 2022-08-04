import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_serverPreview import ServerPreview
from .stream_messages import Messages
from .stream_members import Members
from .stream_channels import Channels
from .stream_roles import Roles

class SourceDiscord(AbstractSource):

    def check_connection(self, _, config) -> Tuple[bool, str]:
        url = "https://discord.com/api/users/@me"
        headers = {"Authorization": f"Bot {config['server_token']}"}
        response = requests.get(url, headers=headers)
        j_response = response.json()
        if "id" not in j_response:
            return False, "missing id"
        if j_response["id"] != config["bot_id"]:
            return False, "wrong id"
        return True, "accepted"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        print(config["initial_timestamp"])
        initial_timestamp = config["initial_timestamp"]
        return [
            ServerPreview(config),
            Channels(config),
            Messages(config, initial_timestamp=initial_timestamp),
            Members(config),
            Roles(config)
        ]
