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
        return {}

    def request_params(self, stream_state: Mapping[str, Any], **_) -> MutableMapping[str, Any]:
        if stream_state:
            return {"startDate": self._cursor_value, "eventType": self.event_id}
        return {"startDate": self.latest_stream_timestamp, "eventType": self.event_id}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        try:
            self._cursor_value = response.json()[0]["eventDate"][:26] # to get rid of +00:00
            lower_response = json.loads(json.dumps(response.json()).lower()) # transform json to lowercase
            yield from lower_response
        except:
            response.json()

    def next_page_token(self, _: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value["eventDate"]


class MintedEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class PurchasedEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class FullfilledEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class FullfilledErrorEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class RequeuedEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class OpenedEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class PackRevealEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class DepositEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class WithdrawEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class SaleEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"


class RoyaltyEvents(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"
