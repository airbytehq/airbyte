from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Dict

import requests
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class PardotStream(HttpStream, ABC):
    url_base = "https://pi.pardot.com/api/"
    primary_key = "id"
    api_version = "4"

    def __init__(self, config: Dict, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = {
            "Pardot-Business-Unit-Id": self.config['pardot_business_unit_id']
        }
        return headers

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "format": "json",
        }
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()['result']
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records
        
class EmailClicks(PardotStream):
    object_name = "emailClick"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"

class Campaigns(PardotStream):
    object_name = "campaign"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class ListMemberships(PardotStream):
    object_name = "listMembership"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Lists(PardotStream):
    object_name = "list"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Opportunities(PardotStream):
    object_name = "opportunity"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class ProspectAccounts(PardotStream):
    object_name = "prospectAccount"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Prospects(PardotStream):
    object_name = "prospect"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Users(PardotStream):
    object_name = "user"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Visits(PardotStream):
    object_name = "visit"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Visitors(PardotStream):
    object_name = "visitor"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class VisitorActivities(PardotStream):
    object_name = "visitorActivity"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    
class Visitors(PardotStream):
    object_name = "visitor"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"
    