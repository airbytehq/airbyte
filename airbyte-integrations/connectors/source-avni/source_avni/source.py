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
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

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
    primary_key = None
    
    def __init__(self, lastdateandtimemodify: str, **kwargs):
            self.logger.info("Into avni stream")
            super().__init__(**kwargs)
            self.lastdateandtimemodify = lastdateandtimemodify
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = {"lastModifiedDateTime": self.lastdateandtimemodify}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}



class Subjects(AvniStream):
        
    def path(self,**kwargs) -> str:
        return "subjects"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["content"]
        yield from data
        
        

class Programs(AvniStream):

    def path(self,**kwargs) -> str:
        return "programEnrolments"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["content"]
        yield from data
        
class ProgramEncounters(AvniStream):
    
    def path(self,**kwargs) -> str:
        return "programEncounters"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["content"]
        yield from data
    
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
            "lastdateandtimemodify":config['lastdateandtimemodify']
        }
        return [Subjects(**stream_kwargs),Programs(**stream_kwargs),ProgramEncounters(**stream_kwargs)]
    
