import time
import requests
from datetime import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class QueueWaitingRoomsStream(HttpStream):
    primary_key = "eventDate"
    url_base = "https://prod-main-net-dashboard-api.azurewebsites.net"
    
    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.company_id = config["company_id"]
        self.latest_stream_timestamp = timestamp_to_unix(config["start_datetime"])

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {}

    def request_params(self, **_) -> MutableMapping[str, Any]:
        return {"since": self.latest_stream_timestamp}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.status_code != 200:
            return []
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class Events(QueueWaitingRoomsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


def timestamp_to_unix(s_timestamp):
    clean_s_timestamp = s_timestamp[:26]
    return int(
        time.mktime(
            datetime.strptime(
                clean_s_timestamp, "%Y-%m-%dT%H:%M:%S.%f"
            ).timetuple()
        )
    )