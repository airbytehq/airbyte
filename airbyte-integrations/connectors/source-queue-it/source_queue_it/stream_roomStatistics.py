import requests
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

from .stream_waitingRooms import WaitingRooms


class RoomStatisticsStream(HttpStream):
    primary_key = ""
    url_base = ""

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.config = config
        self.url_base = config["url_base"]
        self.token = config["token"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {'api-key': self.token}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **_) -> MutableMapping[str, Any]:
        return None

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        yield from [response.json()]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def read_records(self, stream_state: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            yield record


class RoomStatistics(RoomStatisticsStream):

    def stream_slices(self, **kwargs):
        waiting_rooms_stream = WaitingRooms(self.config)
        for waiting_room in waiting_rooms_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"waitingRoomId": waiting_room["EventId"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        waiting_room_id = stream_slice["waitingRoomId"]
        return f"2_0/event/{waiting_room_id}/queue/statistics/summary"
