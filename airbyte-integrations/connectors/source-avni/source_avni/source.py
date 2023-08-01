#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import boto3
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode


class Avni(HttpStream, ABC):

    url_base = "https://app.avniproject.org/api/"
    primary_key = "ID"
    cursor_value = None
    current_page = 0
    last_record = None
    
    def __init__(self, start_date: str, path , auth_token: str, **kwargs):
        super().__init__(**kwargs)

        self.start_date = start_date
        self.auth_token = auth_token
        self.stream=path


class AvniStream(Avni,IncrementalMixin):

    """
    
    This implement diffrent Stream in Source Avni
    
    Api docs : https://avni.readme.io/docs/api-guide
    Api endpoints : https://app.swaggerhub.com/apis-docs/samanvay/avni-external/1.0.0
    """
    def path(self, **kwargs) -> str:
        return self.stream
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"lastModifiedDateTime": self.state["Last modified at"]}
        if next_page_token:
            params.update(next_page_token)
        return params
    
    @property
    def name(self) -> str:
        return self.stream
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        return {"auth-token": self.auth_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        data = response.json()["content"]
        if data:
            self.last_record = data[-1]

        yield from data

    def update_state(self) -> None:

        if self.last_record:
            updated_last_date = self.last_record["audit"]["Last modified at"]
            if updated_last_date>self.state[self.cursor_field[1]]:
                self.state = {self.cursor_field[1]: updated_last_date}
        self.last_record = None
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        total_elements = int(response.json()["totalElements"])
        page_size = int(response.json()["pageSize"])

        if total_elements == page_size:
            self.current_page = self.current_page + 1
            return {"page": self.current_page}

        self.update_state()

        self.current_page = 0

        return None

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> List[str]:
        return ["audit", "Last modified at"]

    @property
    def state(self) -> Mapping[str, Any]:

        if self.cursor_value:
            return {self.cursor_field[1]: self.cursor_value}
        else:
            return {self.cursor_field[1]: self.start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self.cursor_value = value[self.cursor_field[1]]
        self._state = value


class SourceAvni(AbstractSource):
    

    def get_client_id(self):

        url_client = "https://app.avniproject.org/idp-details"
        response = requests.get(url_client)
        response.raise_for_status()
        client = response.json()
        return client["cognito"]["clientId"]

    def get_token(self, username: str, password: str, app_client_id: str) -> str:

        client = boto3.client("cognito-idp", region_name="ap-south-1")
        response = client.initiate_auth(
            ClientId=app_client_id, AuthFlow="USER_PASSWORD_AUTH", AuthParameters={"USERNAME": username, "PASSWORD": password}
        )
        return response["AuthenticationResult"]["IdToken"]
    
    
    def check_connection(self, logger, config) -> Tuple[bool, any]:
    
        username = config["username"]
        password = config["password"]

        try:
            client_id = self.get_client_id()
        except Exception as error:
            return False, str(error) + ": Please connect With Avni Team"

        try:
            
            auth_token = self.get_token(username, password, client_id)
            stream_kwargs = {"auth_token": auth_token, "start_date": config["start_date"]}
            stream = AvniStream(path="subjects",**stream_kwargs).read_records(SyncMode.full_refresh)
            return True, None
        
        except Exception as error:
            return False, error
        
    def generate_streams(self, config: str) -> List[Stream]:
        
        streams = []
        username = config["username"]
        password = config["password"]

        try:
            client_id = self.get_client_id()
        except Exception as error:
            print(str(error) + ": Please connect With Avni Team")
            raise error

        auth_token = self.get_token(username, password, client_id)
        
        endpoints =["subjects","programEnrolments","programEncounters","encounters"]
        for endpoint in endpoints:
            stream_kwargs = {"auth_token": auth_token, "start_date": config["start_date"]}
            stream=AvniStream(path=endpoint,**stream_kwargs)
            streams.append(stream)

        return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        streams = self.generate_streams(config=config)
        return streams