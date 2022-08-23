import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_waitingRooms import WaitingRooms
from .stream_roomStatistics import RoomStatistics

class SourceQueueIt(AbstractSource):

    def check_connection(self, _, config) -> Tuple[bool, str]:
        url = config["url_base"] + "/2_0/event"
        headers = {'api-key': config["token"]}
        response = requests.get(url, headers=headers)
        j_response = response.json()
        if len(j_response) == 0:
            return False, "wrong token"
        return True, "accepted"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            WaitingRooms(config),
            RoomStatistics(config)
        ]
