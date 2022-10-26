#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from pydoc import doc
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from datetime import datetime, timedelta 
from  dateutil.parser import parse

import requests
import asyncio
import base64
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, NoAuth

class SurveyctoStream(HttpStream,  IncrementalMixin, ABC):
    # @TODO: Make server name as a parameter

    primary_key = 'KEY'
    date_format = '%b %d, %Y %H:%M:%S %p'
    dateformat =  '%Y-%m-%dT%H:%M:%S'
    cursor_field = 'CompletionDate'
    _cursor_value = None
   
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.server_name = config['server_name']
        self.form_id = config.get("form_id", [])
        self.start_date = config['start_date']
        #base64 encode username and password as auth token
        user_name_password = f"{config['username']}:{config['password']}"
        self.auth_token = self._base64_encode(user_name_password)

    @property
    def state(self) -> Mapping[str, Any]:
        initial_date = datetime.strptime(self.start_date, self.date_format)
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: initial_date}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], self.dateformat)
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def _base64_encode(self,string:str) -> str:
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    @property
    def url_base(self) -> str:
         return f"https://{self.server_name}.surveycto.com/api/v2/forms/data/wide/json/"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
         return f"{stream_slice['id']}"


    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
       yield from [{"id": id} for id in self.form_id]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
         ix = self.state[self.cursor_field] 
         return {'date': ix.strftime(self.date_format)}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Authorization': 'Basic ' + self.auth_token }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_json = response.json()

        stream_slice = stream_slice.get('id')
        for data in response_json:
            try:
                data["form_id"] = stream_slice
                key = data["KEY"]
                o = key.replace('uuid:', '')
                data["KEY"] = o
               
                yield data
            except Exception as e:
                msg = f"""Encountered an exception parsing schema"""
                self.logger.exception(msg)
                raise e

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            self._cursor_value = datetime.strptime(record[self.cursor_field], self.date_format)
            yield record

# Source
class SourceSurveycto(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        # return [Customers(authenticator=auth), Employees(authenticator=auth)]
        auth = NoAuth()
        return [SurveyctoStream(authenticator=auth, config=config)]

