#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream,IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream

from datetime import datetime


class TokenHeadAuthenticator(AbstractHeaderAuthenticator):

    """
    This is custom class for authentication
    as airbyte does not provid method for authentication process of avni API's
    """
    @property
    def auth_header(self) -> str:
        return self._auth_header

    @property
    def token(self) -> str:
        return self._token

    def __init__(self, token: str, auth_header: str = "auth-token"):
        self._auth_header = auth_header
        self._token = token


class AvniStream(HttpStream, ABC):
    
    url_base = "https://app.avniproject.org/api/"
    primary_key = "ID"
    
    def __init__(self,**kwargs):
            self.logger.info("Into avni stream")
            super().__init__(**kwargs)
            self.cursor_value = None
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class IncrementalAvniStream(AvniStream,IncrementalMixin,ABC):


    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return "Last modified at"
    
    @property
    def state(self) -> Mapping[str, Any]:
        if self.cursor_value:
            return {self.cursor_field: self.cursor_value}
        else:
            return {self.cursor_field: "2020-10-31T01:30:00.000Z"}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self.cursor_value = value[self.cursor_field]
        self._state = value
        
class Subjects(IncrementalAvniStream):
        
    def path(self,**kwargs) -> str:
        return "subjects"
    
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        
        params = {"lastModifiedDateTime": self.state[self.cursor_field]}
        return params   
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["content"]
        yield from data
        
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            audit=record["audit"]
            current_value = audit["Last modified at"]
            cursor_value = self.state[self.cursor_field]
            if current_value:
                print(current_value)
                print(cursor_value)
                format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
                current_datetime = datetime.strptime(current_value, format_string)
                state_datetime = datetime.strptime(cursor_value, format_string)
                if state_datetime < current_datetime:    
                    self.state = {"Last modified at": current_value}
                    print("State has been changed  New value:", self.state[self.cursor_field]) 
            yield record

        

class Programs(AvniStream):

    def path(self,**kwargs) -> str:
        return "programEnrolments"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["content"]
        yield from data

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = {"lastModifiedDateTime": "2020-10-31T01:30:00.000Z"}
        return params   
        
        
class ProgramEncounters(AvniStream):
    
    def path(self,**kwargs) -> str:
        return "programEncounters"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["content"]
        yield from data
        
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = {"lastModifiedDateTime": "2020-10-31T01:30:00.000Z"}
        return params  
    
class SourceAvni(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        print("check connection")
        auth_token=config['AUTH_TOKEN']
        url = 'https://app.avniproject.org/api/subjects'
        params = {
             'lastModifiedDateTime': '2100-10-31T01:30:00.000Z'
                }
        headers = {
             'accept': 'application/json',
             'auth-token': auth_token
             }
        response = requests.get(url, params=params, headers=headers)
        if(response.status_code==200):
            return True, None
        else:
            return False, None
        
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenHeadAuthenticator(token = config["AUTH_TOKEN"])
        stream_kwargs = {
            "authenticator": authenticator,
        }
        return [Subjects(**stream_kwargs),Programs(**stream_kwargs),ProgramEncounters(**stream_kwargs)]
    
