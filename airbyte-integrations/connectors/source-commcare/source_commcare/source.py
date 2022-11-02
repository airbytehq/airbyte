#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from time import strptime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime, timedelta

import requests
from urllib.parse import parse_qs
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

# Basic full refresh stream
class CommcareStream(HttpStream, ABC):
    url_base = "https://www.commcarehq.org/a/sc-baseline/api/v0.5/"

    # These class variables save state 
    # forms holds form ids and we filter cases which contain one of these form ids
    # last_form_date stores the date of the last form read so the next cycle for forms and cases starts at the same timestamp
    forms = set()
    last_form_date = None

    @property
    def dateformat(self):
        return '%Y-%m-%dT%H:%M:%S.%f'

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        params = {'format': 'json'}
        return params


class Application(CommcareStream):
    primary_key = "id"
    def __init__(self, app_id, **kwargs):
        super().__init__(**kwargs)
        self.app_id = app_id

    def path(
    self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
) -> str:
        return f"application/{self.app_id}/"
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        params = {
            'format': 'json', 
            'extras' : 'true'
        }
        return params
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()



class IncrementalStream(CommcareStream, IncrementalMixin):
    cursor_field = 'indexed_on'
    _cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], self.dateformat)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            # Server returns status 500 when there are no more rows.
            # raise an error if server returns an error
            response.raise_for_status()
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



# Airbyte orders streams in alpha order but since we have dependent peers and we need to 
# pull Form before Case, we call this stream FormCase so Airbyte pulls it after Form
class FormCase(IncrementalStream):
    cursor_field = 'indexed_on'
    primary_key = "case_id"

    def __init__(self, start_date, app_id, **kwargs):
        super().__init__(**kwargs)
        self._cursor_value = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "case"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        # start date is what we saved for forms
        ix = self.state[self.cursor_field] #if self.cursor_field in self.state else (CommcareStream.last_form_date or self.initial_date)
        params = {
            'format': 'json', 
            'indexed_on_start': ix.strftime(self.dateformat), 
            'order_by': 'indexed_on', 
            'limit': '5000'
        }
        if next_page_token:
            params.update(next_page_token)
        return params

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            found = False
            for f in record['xform_ids']:
                if f in CommcareStream.forms:
                    found = True
                    break
            if found:
                self._cursor_value = datetime.strptime(record[self.cursor_field], self.dateformat)
                yield record

        # This cycle of pull is complete so clear out the form ids we saved for this cycle
        # CommcareStream.forms.clear()
        # self._cursor_value = CommcareStream.last_form_date
        print(f'######============= CASE READ DONE {self.state[self.cursor_field]} ===============')


class Form(IncrementalStream):
    cursor_field = 'indexed_on'
    primary_key = "id"
    def __init__(self, start_date, app_id, **kwargs):
        super().__init__(**kwargs)
        self.app_id = app_id
        self._cursor_value = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
        
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "form"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        ix = self.state[self.cursor_field] #if self.cursor_field in self.state else self.initial_date
        params = {
            'format': 'json', 
            'app_id': self.app_id, 
            'indexed_on_start': ix.strftime(self.dateformat), 
            'order_by': 'indexed_on', 
            'limit': '1000'
        }
        if next_page_token:
            params.update(next_page_token)
        return params

    
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            self._cursor_value = datetime.strptime(record[self.cursor_field], self.dateformat)
            CommcareStream.forms.add(record['id'])
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
        app_args = { **args, 'app_id': config['app_id']}
        form_args = { **args, 'app_id': config['app_id'], 'start_date': config['start_date']}
        return [
            Application(**app_args),
            Form(**form_args),       
            FormCase(**form_args)
        ]

