from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from datetime import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
# import ndjson
import json

# Basic full refresh stream
class TimelyIntegrationStream(HttpStream, ABC):

    url_base = "https://api.timelyapp.com/1.1/"

    def __init__(self, account_id:str, start_date:str, bearer_token:str,**kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.start_date = start_date
        self.bearer_token = bearer_token

    def request_params(self, 
                    stream_state: Mapping[str, any], 
                    stream_slice: Mapping[str, Any]= None,
                    next_page_token: Mapping[str, Any]= None) -> MutableMapping[str, Any]:
        return {"account_id":self.account_id}
    
    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        bearer_token = self.bearer_token
        event_headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        return event_headers

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        # input = [response.json()]
        # data = json.loads(input)
        # output = ndjson.dumps(data)
        # return output
        return response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

#Incremental

class events(TimelyIntegrationStream):
    
    primary_key = "id"
    
    def path(self, **kwargs) -> str:
        account_id = self.account_id
        start_date = self.start_date
        upto = datetime.today().strftime('%Y-%m-%d')
        return f"{account_id}/events?since={start_date}&upto={upto}"

class SourceTimelyIntegration(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        account_id = config["account_id"]
        start_date = config["start_date"]
        bearer_token = config["bearer_token"]

        headers = {"Authorization":f"Bearer {bearer_token}","Content-Type":"application/json"}
        url = f"https://api.timelyapp.com/1.1/{account_id}/events?since={start_date}&upto=2022-05-01"

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        #authroization = TokenAuthenticator(config["bearer_token"])

        args={
            "bearer_token": config["bearer_token"],
            "account_id":config["account_id"],
            "start_date":config["start_date"]
        }
        return [events(**args)]