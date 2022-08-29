import time
import requests
from datetime import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class EventsStream(HttpStream):
    primary_key = "id"
    cursor_field = "eventDate"
    url_base = "https://prod-main-net-dashboard-api.azurewebsites.net"
    
    def __init__(self, config: Mapping[str, Any], **_):
        super().__init__()
        self.company_id = config["company_id"]
        self.latest_stream_timestamp = config["start_datetime"]

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {}

    def request_params(self, stream_state: Mapping[str, Any], **_) -> MutableMapping[str, Any]:
        if stream_state:
            return {"startDate": self._cursor_value}
        return {"startDate": self.latest_stream_timestamp}

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        if response.text:
            self._cursor_value = response.json()[0]["eventDate"][:26] # [:26] to get rid of +00:00
        yield from response.json()

    def next_page_token(self, _: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def read_records(self, stream_state: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            yield  {k.lower(): v for k, v in record.items()} # convert keys to lower case because redshift problem

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value["eventDate"]


class Events(EventsStream):
    def path(self, **_) -> str:
        return f"api/company/{self.company_id}/search"
