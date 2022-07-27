import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_serverPreview import ServerPreview
from .stream_channelMessages import ChannelMessages

class SourceDiscord(AbstractSource):

    def check_connection(self, _, config) -> Tuple[bool, Any]:
        url = "https://discord.com/api/users/@me"
        headers = {"Authorization": f"Bot {config['server_token']}"}
        response = requests.get(url, headers=headers)
        j_response = response.json()
        if j_response["id"] != config["bot_id"]:
            return False, None
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        initial_timestamp = config["initial_timestamp"]
        return [
            ServerPreview(config),
            ChannelMessages(config, initial_timestamp=initial_timestamp)
        ]
