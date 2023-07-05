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
import boto3

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
    
    def __init__(self,lastModifiedDateTime:str, **kwargs):
            super().__init__(**kwargs)
            self.cursor_value = None
            self.current_page=0
            self.lastModifiedDateTime=lastModifiedDateTime
            self.last_record=None
    
    
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        
        params = {"lastModifiedDateTime": self.state[self.cursor_field]}
        if next_page_token:
            params.update(next_page_token)
        return params   
    
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        
        data = response.json()["content"]
        if data:
            self.last_record = data[-1]
            
        yield from data
        
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        
        total_elements = int(response.json()["totalElements"])
        total_pages = int(response.json()["totalPages"])
        page_size = int(response.json()["pageSize"])

        if(total_elements==page_size):
            self.current_page = self.current_page + 1
            return {"page": self.current_page}
        
        if(self.last_record):
            
            updated_last_date = self.last_record["audit"]["Last modified at"]
            self.state = {"Last modified at": updated_last_date}
            self.last_record=None
            
        self.current_page=0
        
        return None 


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
            return {self.cursor_field: self.lastModifiedDateTime}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self.cursor_value = value[self.cursor_field]
        self._state = value


class Subjects(IncrementalAvniStream):
        
    def path(self,**kwargs) -> str:
        return "subjects"            
    

class Programs(IncrementalAvniStream):

    def path(self,**kwargs) -> str:
        return "programEnrolments"
    

class ProgramEncounters(IncrementalAvniStream):
    
    def path(self,**kwargs) -> str:
        return "programEncounters"
    
    
class SubjectEncounters(IncrementalAvniStream):
    
    def path(self,**kwargs) -> str:
        return "encounters"
    
        
class SourceAvni(AbstractSource):
    
    def get_client_id(self):
        
        url_client="https://app.avniproject.org/idp-details"
        client = requests.get(url_client).json()
        return client['cognito']['clientId']
    
      
    def get_token(self,username: str, password: str, app_client_id: str) -> str:
        
        client = boto3.client('cognito-idp',region_name='ap-south-1')
        response = client.initiate_auth(
            ClientId=app_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            }
        )
        
        return response['AuthenticationResult']['IdToken']
    
    
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        
        username=config["username"]
        password=config["password"]
        client_id = self.get_client_id()
        auth_token= self.get_token(username,password,client_id)
        
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
        
        username=config["username"]
        password=config["password"]
        client_id=self.get_client_id()
        auth_token= self.get_token(username,password,client_id)
        authenticator = TokenHeadAuthenticator(token = auth_token)
        
        stream_kwargs = {
        "authenticator": authenticator,
        "lastModifiedDateTime":config["lastModifiedDateTime"]
        }
        
        return [Subjects(**stream_kwargs),Programs(**stream_kwargs),ProgramEncounters(**stream_kwargs),SubjectEncounters(**stream_kwargs)]
    
