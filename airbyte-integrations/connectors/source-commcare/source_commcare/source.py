#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from urllib.parse import parse_qs
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

# Basic full refresh stream
class CommcareStream(HttpStream, ABC):
    url_base = "https://www.commcarehq.org/a/sc-baseline/api/v0.5/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            # Server returns status 500 when there are no more rows.
            # raise an error if server returns an error
            response.raise_for_status()
            # print(response.json()['meta'])
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


class Case(CommcareStream):
    primary_key = "case_id"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "case"

class Form(CommcareStream):
    primary_key = "id"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "form"


# Source
class SourceCommcare(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        if not 'api-key' in config:
            # print("Returning No")
            return False, None
        # print("Returning Yes")
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config['api-key'], auth_method="ApiKey")  
        return [
            Case(authenticator=auth),
            Form(authenticator=auth)       
        ]
