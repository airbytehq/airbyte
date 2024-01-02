#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator

def _auth_from_config(config):
    try:
        if config["api_key"]:
            return BasicHttpAuthenticator(username=config["api_key"], password=None, auth_method="Basic")
        else:
            print("Auth type was not configured properly")
            return None
    except Exception as e:
        print(f"{e.__class__} occurred, there's an issue with credentials in your config")
        raise e
    

class SourceLever(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = _auth_from_config(config)
            _ = authenticator.get_auth_header()
        except Exception as e:
            return False, str(e)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = _auth_from_config(config)

        incremental_stream_params = {
            "authenticator":authenticator, 
            "start_date": '1990-01-01'
        }

        opportunity_steam = Opportunities(**incremental_stream_params)

        return [
            opportunity_steam,
            Offers(**incremental_stream_params, parent_stream=opportunity_steam),
            Feedback(**incremental_stream_params, parent_stream=opportunity_steam),
            Interviews(**incremental_stream_params, parent_stream=opportunity_steam),
            Notes(**incremental_stream_params, parent_stream=opportunity_steam),
            Panels(**incremental_stream_params, parent_stream=opportunity_steam),
            Requisitions(authenticator=authenticator),
            Users(authenticator=authenticator),
            Stages(authenticator=authenticator),
            Postings(authenticator=authenticator),
            ArchiveReasons(authenticator=authenticator),
            Tags(authenticator=authenticator),
            Sources(authenticator=authenticator),
            RequisitionFields(authenticator=authenticator),
        ]

class LeverStream(HttpStream, ABC):
    page_size = 100
    stream_params = {}
    
    API_VERSION = "v1"
    base_url = "https://api.lever.co"

    @property
    def url_base(self) -> str:
        return f"{self.base_url}/{self.API_VERSION}/"
    

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if response_data.get("hasNext"):
            return {"offset": response_data["next"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        params.update(self.stream_params)
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, stream_slice:Mapping[str, Any],  **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]

"""
TODO: Temp workaround.

For incremental substreams to work, make sure the connector is set up with the state:
[
  {
    "streamDescriptor": {
      "name": "opportunities"
    },
    "streamState": {
      "updatedAt": 631152000000
    }
  }
]

There is an issue where an empty state {} will cause the parent Opportunity stream to update state wrongly.
The state after the first run of an incremental stream will become: 
[
  {
    "streamDescriptor": {
      "name": "opportunities"
    },
    "streamState": {
      "updatedAt": "None"
    }
  }
]

This breaks the implementation we have below since we **reasonably** assume `updatedAt: int`. By setting the initial state
to a valid `updatedAt: number` value, we can work around this issue and subsequent updates will work correctly using the Opportunity's latest record
"""
# 
# 
class IncrementalLeverStream(LeverStream, IncrementalMixin):
    state_checkpoint_interval = 100
    cursor_field = "updatedAt"

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_timestamp = int(pendulum.parse(start_date).timestamp()) * 1000
        self._cursor_value = None
        self._initial_cursor_value = None
    
    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: str(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        if value[self.cursor_field] and value[self.cursor_field] != 'None' :
            self._cursor_value = value[self.cursor_field]
            if not self._initial_cursor_value:
                self._initial_cursor_value = value[self.cursor_field]
        else: 
            self._cursor_value = self._start_timestamp
            self._initial_cursor_value = self._start_timestamp

    """
    We use this function so sub streams can reference the inital state the parent stream started with e.g:
    - initial cursor value = 2023-01-01
    - after stream completes, cursor value = now()
    substream run should use initial cursor value(2023-01-01). Using now() will give us too little records
    """
    def initial_state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._initial_cursor_value}

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            latest_record_date = record[self.cursor_field]
            if self._cursor_value and record[self.cursor_field]:
                self._cursor_value = max(int(self._cursor_value), int(latest_record_date))
            yield record

    
    def request_params(self, stream_state: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        stream_state_timestamp = stream_state.get(self.cursor_field, 0) or 0
        params["updated_at_start"] = max(int(stream_state_timestamp), self._start_timestamp)
        print("> Request params:", params)

        return params

class Opportunities(IncrementalLeverStream):
    """
    Opportunities stream: https://hire.lever.co/developer/documentation#opportunities
    """

    use_cache = True
    primary_key = "id"
    stream_params = {"confidentiality": "all", "expand": ["contact", "applications"]}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "opportunities"

class Requisitions(LeverStream):
    # https://hire.lever.co/developer/documentation#requisitions
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "requisitions"  

class Users(LeverStream):
    """
    Users stream: https://hire.lever.co/developer/documentation#users
    """
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "users"

class Stages(LeverStream):
    """
    Stages stream: https://hire.lever.co/developer/documentation#stages
    """
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "stages"
    
class Postings(LeverStream):
    """
    Postings stream: https://hire.lever.co/developer/documentation#postings
    """
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "postings"

class Tags(LeverStream):
    """
    Tags stream: https://hire.lever.co/developer/documentation#tags
    """
    primary_key = "text"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "tags"

class Sources(LeverStream):
    """
    Sources stream: https://hire.lever.co/developer/documentation#sources
    """
    primary_key = "text"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "sources"
    
class RequisitionFields(LeverStream):
    """
    Requisiton fields stream: https://hire.lever.co/developer/documentation#requisition-fields
    """
    primary_key = "text"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "requisition_fields"

class ArchiveReasons(LeverStream):
    """
    Archive Reasons stream: https://hire.lever.co/developer/documentation#archive-reasons
    """
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "archive_reasons"


# Basic Sub streams using Opportunity id
class OpportunitySubStream(LeverStream, ABC):

    def __init__(self, start_date:str, parent_stream:IncrementalLeverStream, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self.parent_stream = parent_stream

    
    
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"opportunities/{stream_slice['opportunity_id']}/{self.name}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in super().stream_slices(**kwargs):
            for opportunity in self.parent_stream.read_records(stream_state=self.parent_stream.initial_state(), stream_slice=stream_slice, sync_mode=SyncMode.incremental):
                yield {"opportunity_id": opportunity["id"]}
    

    def parse_response(self, response: requests.Response, stream_slice:[Mapping[str, Any]], **kwargs) -> Iterable[Mapping]:
        records = response.json()["data"]

        # https://airbytehq.slack.com/archives/C027KKE4BCZ/p1696509193002769
        # Fixes the issue where an empty array returned was not refreshing our heartbeat and causing a timeout issue.
        # if records = [], we will add an empty object in the array
        if not records:
            records = [{}]
        
        # Adds the parent stream's ID in each substream record
        for record in records:
            record["opportunity"] = stream_slice["opportunity_id"]
        yield from records
        

class Offers(OpportunitySubStream):
    """
    Offers stream: https://hire.lever.co/developer/documentation#list-all-offers
    """
    primary_key = "id"

class Feedback(OpportunitySubStream):
    """
    Feedback stream: https://hire.lever.co/developer/documentation#list-all-feedback
    """
    primary_key = "id"

class Interviews(OpportunitySubStream):
    """
    Interviews stream: https://hire.lever.co/developer/documentation#list-all-interviews
    """
    primary_key = "id"

class Panels(OpportunitySubStream):
    """
    Panels stream: https://hire.lever.co/developer/documentation#list-all-panels
    """
    primary_key = "id"

class Notes(OpportunitySubStream):
    """
    Notes stream: https://hire.lever.co/developer/documentation#list-all-notes
    """
    primary_key = "id"
