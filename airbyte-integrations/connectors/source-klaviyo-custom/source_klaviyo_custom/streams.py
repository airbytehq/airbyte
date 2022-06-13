from datetime import datetime,timedelta,timezone

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams.core import IncrementalMixin

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

    @staticmethod
    def _add_dict_to_record(record,dict):
        record.update(dict)
        return record
   
class IncrementalStream(KlaviyoCustomStream,IncrementalMixin):
    DATE_COLUMN_NAME = "GETDATE_UTC"
    DATETIME_COLUMN_NAME = "GETDATETIME_UTC"

    @property
    def state(self):
        return {self.cursor_field:self._cursor_value}

    @state.setter
    def state(self,value):
        return self._cursor_value

class Lists(KlaviyoCustomStream):
    
    primary_key = "list_id"

    def __init__(self, authenticator = None):
        super().__init__(authenticator)
        self._list_url = "https://a.klaviyo.com/api/v2/lists"


    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return "v2/lists"


class ListMembers(IncrementalStream):
    
    
    primary_key = ["id",IncrementalStream.DATE_COLUMN_NAME]
    cursor_field = IncrementalStream.DATE_COLUMN_NAME
    REQ_PAGINATION_KEY = RESP_PAGINATION_KEY = "marker"
    use_cache = True

    def __init__(self, list_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_id = list_id
        self.get_date = datetime.now(timezone.utc)
        self._get_date_str = self.get_date.strftime("%Y-%m-%d")
        self._get_datetime_str = self.get_date.isoformat()
        self._time_dict = {
            self.DATE_COLUMN_NAME:self._get_date_str,
            self.DATETIME_COLUMN_NAME:self._get_datetime_str
        }
        self._cursor_value = self._get_date_str
        self.page_count = 0

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return f"v2/group/{self.list_id}/members/all"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params[self.REQ_PAGINATION_KEY] = next_page_token[self.RESP_PAGINATION_KEY]
        return params


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from [self._add_dict_to_record(record,self._time_dict) for record in response.json()["records"]]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if self.RESP_PAGINATION_KEY in data:
            self.page_count += 1
            self.logger.info(f"Got {self.page_count} pages for {self.__class__.__name__}")
            return {self.RESP_PAGINATION_KEY: data[self.RESP_PAGINATION_KEY]}
            # return None
        else:
            return None


class ListExclusions(IncrementalStream):
    
    primary_key = ["id",IncrementalStream.DATE_COLUMN_NAME]
    cursor_field = IncrementalStream.DATE_COLUMN_NAME
    REQ_PAGINATION_KEY = RESP_PAGINATION_KEY = "marker"
    use_cache = True

    def __init__(self, list_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_id = list_id
        self.get_date = datetime.now(timezone.utc)
        self._get_date_str = self.get_date.strftime("%Y-%m-%d")
        self._get_datetime_str = self.get_date.isoformat()
        self._time_dict = {
            self.DATE_COLUMN_NAME:self._get_date_str,
            self.DATETIME_COLUMN_NAME:self._get_datetime_str
        }
        self._cursor_value = self._get_date_str
        self.page_count = 0

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return f"v2/list/{self.list_id}/exclusions/all"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params[self.REQ_PAGINATION_KEY] = next_page_token[self.RESP_PAGINATION_KEY]
        return params


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from [self._add_dict_to_record(record,self._time_dict) for record in response.json()["records"]]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if self.RESP_PAGINATION_KEY in data:
            self.page_count += 1
            self.logger.info(f"Got {self.page_count} pages for {self.__class__.__name__}")
            return {self.RESP_PAGINATION_KEY: data[self.RESP_PAGINATION_KEY]}
            # return None
        else:
            return None

class Profiles(IncrementalStream,HttpSubStream):
    
    primary_key = "id"
    cursor_field = "created"

    def __init__(self,exclude_list:ListExclusions,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclude_list = exclude_list
        self.get_date = datetime.now(timezone.utc)
        self._get_date_str = self.get_date.strftime("%Y-%m-%d")
        self._get_datetime_str = self.get_date.isoformat()
        self._time_dict = {
            self.DATE_COLUMN_NAME:self._get_date_str,
            self.DATETIME_COLUMN_NAME:self._get_datetime_str
        }
        self._cursor_value = self._get_datetime_str

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        id = stream_slice
        self.item_order += 1
        self.logger.info(f"Looking at id {id}. #{self.item_order} out of {self.parent_length}")
        return f"v1/person/{id}"
    
    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        id_set = []
        for parent in (self.parent,self.exclude_list):
            parent_stream_slices = parent.stream_slices(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
            )
            for stream_slice in parent_stream_slices:
                parent_records = parent.read_records(
                    sync_mode=SyncMode.full_refresh
                    , cursor_field=cursor_field
                    , stream_slice=stream_slice
                    , stream_state=stream_state
                )
                id_set.extend([item["id"] for item in parent_records])
        self.item_order = 0
        self.parent_length = len(id_set)
        yield from id_set

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield self._add_dict_to_record(response.json(),self._time_dict)

        