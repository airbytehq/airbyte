import json
import requests
from datetime import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class EventsStream(HttpStream):
    primary_key = "id"
    cursor_field = "eventDate"
    url_base = "https://prod-main-net-dashboard-api.azurewebsites.net"
    
    def __init__(self, config: Mapping[str, Any], event_id: str, **_):
        super().__init__()
        self.company_id = config["company_id"]
        self.event_id = event_id
        self.latest_stream_timestamp = config["start_datetime"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        print("############request_headers", "NO REQUEST HEADERS")
        return {}

    def request_params(self, stream_state: Mapping[str, Any], **_) -> MutableMapping[str, Any]:
        if stream_state:
            print("############request_params", {"startDate": self._cursor_value, "eventType": self.event_id})
            return {"startDate": self._cursor_value, "eventType": self.event_id}
        print("############request_params", {"startDate": self._cursor_value, "eventType": self.event_id})
        return {"startDate": self.latest_stream_timestamp, "eventType": self.event_id}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        print("############parse_response", "PARSING RESPONSE")
        self._cursor_value = response.json()[0]["eventDate"][:26] # [:26] to get rid of +00:00
        lower_response = json.loads(json.dumps(response.json()).lower()) # transform json to lowercase
        print("############parse_response", self._cursor_value)
        yield from lower_response

    def next_page_token(self, _: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value["eventDate"]


class PurchasedEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class PackRevealEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"
