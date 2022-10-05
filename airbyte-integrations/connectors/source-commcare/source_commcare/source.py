#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime

import requests
from urllib.parse import parse_qs
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

# Basic full refresh stream
class CommcareStream(HttpStream, IncrementalMixin, ABC):
    url_base = "https://www.commcarehq.org/a/sc-baseline/api/v0.5/"
    forms = {}
    dateformat = '%Y-%m-%dT%H:%M:%S.%f'
    initial_date = datetime(2022,1,1,0,0,0)
    last_form_date = initial_date
    cursor_field = 'indexed_on'
    _cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.initial_date}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], self.dateformat)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            # Server returns status 500 when there are no more rows.
            # raise an error if server returns an error
            response.raise_for_status()
            # print(response.json()['meta'])
            meta = response.json()['meta']
            return parse_qs(meta['next'][1:])
        except:
            return None
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        params = {'format': 'json'}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for o in iter(response.json()['objects']):
            yield o
        return None


class FormCase(CommcareStream):
    cursor_field = 'indexed_on'
    primary_key = "case_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "case"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        # start date is what we saved for forms
        ix = self.state[self.cursor_field] if self.cursor_field in self.state else super().last_form_date
        params = {
            'format': 'json', 
            'indexed_on_start': ix.strftime(super().dateformat), 
            'order_by': 'indexed_on', 
            'limit': '5000'
        }
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for o in iter(response.json()['objects']):
            found = False
            for f in o['xform_ids']:
                if f in super().forms:
                    found = True
                    break
            if found:
                yield o
        return None

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            yield record

        super().forms.clear()
        self._cursor_value = super().last_form_date
        print(f'######============= CASE READ DONE {self.state[self.cursor_field]} ===============')


class Form(CommcareStream):
    cursor_field = 'indexed_on'
    primary_key = "id"
    def __init__(self, app_id, **kwargs):
        super().__init__(**kwargs)
        self.app_id = app_id
        
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "form"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        ix = self.state[self.cursor_field] if self.cursor_field in self.state else super().initial_date
        params = {
            'format': 'json', 
            'app_id': self.app_id, 
            'indexed_on_start': ix.strftime(super().dateformat), 
            'order_by': 'indexed_on', 
            'limit': '1000'
        }
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for o in iter(response.json()['objects']):
            super().forms[o['id']] = 1
            yield o
        return None
    
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            self._cursor_value = datetime.strptime(record[self.cursor_field], self.dateformat)
            yield record

        print(f'######============= FORM READ DONE {self.state[self.cursor_field]} ===============')
        CommcareStream.last_form_date = self._cursor_value

# Source
class SourceCommcare(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        if not 'api_key' in config:
            # print("Returning No")
            return False, None
        # print("Returning Yes")
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config['api_key'], auth_method="ApiKey") 
        args = {
            "authenticator": auth,
        }
        with_appid = { **args, 'app_id': config['app_id']}

        return [
            Form(**with_appid),       
            FormCase(**args)
        ]

