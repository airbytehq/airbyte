import inspect
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.models.airbyte_protocol import SyncMode

import requests
from requests.auth import AuthBase
from requests import models

class KlaviyoAuthenticator(AuthBase):

    def __init__(self,api_key) -> None:
        self._api_key = api_key
    
    def __call__(self, r: models.PreparedRequest) -> models.PreparedRequest:
        r.prepare_url(r.url, {
            "api_key":self._api_key
        })
        return r

# Basic full refresh stream
class KlaviyoCustomStream(HttpStream, ABC):
    
    url_base = "https://a.klaviyo.com/api/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json()
   

class Lists(KlaviyoCustomStream):
    
    primary_key = "list_id"

    def __init__(self, authenticator = None):
        super().__init__(authenticator)
        self._list_url = "https://a.klaviyo.com/api/v2/lists"


    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return "v2/lists"

    def use_cache(self):
        return True


class ListMembers(KlaviyoCustomStream,HttpSubStream):
    
    primary_key = "id"

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:

        id = stream_slice
        return f"v2/group/{id}/members/all"
    
    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        parent_stream_slices = list(parent_stream_slices)
        parent_len = len(parent_stream_slices)
        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            print(f"Doing function {inspect.currentframe().f_code.co_name} for {self.name} with slice #{stream_slice} out of {parent_len}")
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh
                , cursor_field=cursor_field
                , stream_slice=stream_slice
                , stream_state=stream_state
            )
            list_ids = {item["list_id"] for item in parent_records}
        yield from list_ids

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json()["records"]

    def use_cache(self):
        return True

class Profiles(KlaviyoCustomStream,HttpSubStream):
    
    primary_key = "id"

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:

        id = stream_slice
        self.item_order += 1
        self.logger.info(f"Looking at id {id}. #{self.item_order} out of {self.parent_length}")
        return f"v1/person/{id}"
    
    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        id_set = set()
        parent_stream_slices = list(parent_stream_slices)
        len_parent = len(parent_stream_slices)
        counter = 0
        for stream_slice in parent_stream_slices:
            counter += 1
            self.logger.info(f"Doing function {inspect.currentframe().f_code.co_name} for {self.parent.name} with slice #{counter} out of {len_parent}")
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh
                , cursor_field=cursor_field
                , stream_slice=stream_slice
                , stream_state=stream_state
            )
            local_id_set = {item["id"] for item in parent_records}
            id_set.update(local_id_set)
        self.parent_length = len(list(id_set))
        self.item_order = 0
        yield from id_set

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield response.json()