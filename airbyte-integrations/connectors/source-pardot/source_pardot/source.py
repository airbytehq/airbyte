#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from .api import Pardot


AUTH_URL = "https://pi.pardot.com/api/login/version/3"
ENDPOINT_BASE = "https://pi.pardot.com/api/"
REFRESH_URL = "https://login.salesforce.com/services/oauth2/token"

# Basic full refresh stream
class PardotStream(HttpStream, ABC):
    url_base = "https://pi.pardot.com/api/"
    primary_key = "id"
    api_version = "4"

    def __init__(self, config: Dict, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = {
            "Pardot-Business-Unit-Id": self.config['pardot_business_unit_id']
        }
        return headers

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "format": "json",
        }
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()['result']
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records
        
class EmailClick(PardotStream):
    object_name = "emailClick"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"

# Source
class SourcePardot(AbstractSource):
    
    @staticmethod
    def _get_pardot_object(config: Mapping[str, Any]) -> Pardot:
        pardot = Pardot(**config)
        pardot.login()
        return pardot

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        _ = self._get_pardot_object(config)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        pardot = self._get_pardot_object(config)
        auth = TokenAuthenticator(pardot.access_token)
        args = {'authenticator': auth, 'config': config}
        return [EmailClick(**args)]
