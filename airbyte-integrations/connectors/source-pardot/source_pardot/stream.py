from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Dict, List

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class PardotStream(HttpStream, ABC):
    url_base = "https://pi.pardot.com/api/"
    api_version = "4"
    time_filter_template = "%Y-%m-%dT%H:%M:%SZ"
    primary_key = None

    def __init__(self, config: Dict, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        records = response.json().get('result', [])
        if records.get(self.data_key, []):
            return {self.filter_param: records[self.data_key][-1][self.cursor_field]}

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
        start_date = self.config.get('start_date', None)
        if start_date:
            params.update({'created_after': pendulum.parse(start_date, strict=False).strftime(self.time_filter_template)})
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        print(response.text)
        json_response = response.json().get('result', [])
        records = json_response.get(self.data_key, []) if self.data_key is not None else json_response
        yield from records
    
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"

    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        if stream_state:
            for record in records_slice:
                if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice
        
class PardotIdReplicationStream(PardotStream):
    primary_key = "id"
    cursor_field = "id"
    filter_param = "id_greater_than"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}
class EmailClicks(PardotIdReplicationStream):
    object_name = "emailClick"
    data_key = "emailClick"

class VisitorActivities(PardotIdReplicationStream):
    object_name = "visitorActivity"
    data_key = "visitor_activity"

class Campaigns(PardotStream):
    object_name = "campaign"
    
class ListMemberships(PardotStream):
    object_name = "listMembership"
    
class Lists(PardotStream):
    object_name = "list"
    
class Opportunities(PardotStream):
    object_name = "opportunity"
    
class ProspectAccounts(PardotStream):
    object_name = "prospectAccount"
    
class Prospects(PardotStream):
    object_name = "prospect"
    
class Users(PardotStream):
    object_name = "user"
    
class Visits(PardotStream):
    object_name = "visit"
    
class Visitors(PardotStream):
    object_name = "visitor"
    
class Visitors(PardotStream):
    object_name = "visitor"
    