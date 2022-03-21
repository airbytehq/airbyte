#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import request

import pdb
import requests
from requests.auth import HTTPBasicAuth
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
# from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .helpers import Helpers
from . import state_code_list


# Basic full refresh stream
class Prices(HttpStream, ABC):
    url_base = "https://api.collectapi.com/"

    primary_key = None

    def __init__(self, state_code: str, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.state_code = state_code
        self.api_key = api_key


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
    self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return 'gasPrice/stateUsaPrice'

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        return {
            "authorization": f"{self.api_key}",
            "content-type": "application/json",
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        

        return {"state": self.state_code}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        
        return [response.json()]



# Source
class SourceGasPrices(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
            api_key = config["api_key"]
            state = config["state"]

            if state not in state_code_list.STATE_CODE_LIST:
                return False, "Not a valid USA State code"
            
            try:
                Helpers.get_states(state, api_key)
            except Exception as e:
                return False, str(e)
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Prices(config["state"], config["api_key"])]
