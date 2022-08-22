import requests
from typing import Any, Mapping, Iterable, Optional

from airbyte_cdk.sources.streams.http import HttpStream


class QueueWaitingRoomsStream(HttpStream):
    primary_key = ""
    url_base = ""
    
    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.url_base = config["url_base"]
        self.token = config["token"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {'api-key': self.token}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class WaitingRooms(QueueWaitingRoomsStream):
    def path(self, **_) -> str:
        return f"2_0/event"
