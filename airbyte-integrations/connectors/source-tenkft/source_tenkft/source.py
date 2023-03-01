#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pandas as pd
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from ratelimit import limits
from shared import get_vault_secret_client


# Basic full refresh stream
class TenkftStream(HttpStream):

    API_KEY = None

    def get_api_base_url(self):
        return "https://api.rm.smartsheet.com"

    def get_api_key(self):
        global API_KEY
        if not API_KEY:
            secret_client = get_vault_secret_client()
            API_KEY = secret_client.get_secret("10k-feet-api-token").value
        return API_KEY

    @limits(calls=500, period=60)
    def call_url(self, url):
        print(f"GET: {url}")
        headers = {"auth": self.get_api_key()}
        response = requests.get(url, headers)
        return response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class Users(TenkftStream):
    primary_key: Optional[str] = id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        base_url = self.get_api_base_url()
        return self.call_url(f"{base_url}/api/v1/users?per_page=1000")


# Source
class SourceTenkft(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Users()]
