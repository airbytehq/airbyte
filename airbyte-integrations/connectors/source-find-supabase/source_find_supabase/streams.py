import json
import requests
from datetime import datetime
from typing import Any, Mapping, Iterable, Optional, MutableMapping

from airbyte_cdk.sources.streams.http import HttpStream


class FindSupabaseStream(HttpStream):

    primary_key = "id"
    cursor_field = "offset"
    url_base = ""
    
    def __init__(self, config: Mapping[str, Any], table_name: str, **_):
        super().__init__()
        self.anon_public_key = config["anon_public_key"]
        self.url_base = config["project_url"]
        self.limit = int(config["limit"])
        self._cursor_value = 0
        self.table_name = table_name

    def request_headers(self, **_) -> Mapping[str, Any]:
        return {
            "apikey": self.anon_public_key,
            "Authorization": f"Bearer {self.anon_public_key}"
        }

    def request_params(self, next_page_token: Mapping[str, Any], **_) -> MutableMapping[str, Any]:
        if not next_page_token:
            return {
                "limit": self.limit
            }
        else:
            return next_page_token

    def parse_response(self, response: requests.Response, **_) -> Iterable[Mapping]:
        self._cursor_value = self._cursor_value + len(response.json())
        yield from response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if len(response.json()) < self.limit:
            return None
        else:
            return {
                "offset": self._cursor_value + self.limit,
                "limit": self.limit
            }

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value["offset"]


class UnpackedItems(FindSupabaseStream):
    def path(self, **_) -> str:
        return f"rest/v1/{self.table_name}"