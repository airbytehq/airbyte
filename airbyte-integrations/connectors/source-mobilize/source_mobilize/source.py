#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

#import os
import petl
import re
import requests
from requests import request as _request
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import urllib

#from parsons_utilities.mobilize_america import MobilizeAmerica
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

class Organizations(HttpStream):
    # Set this as a noop.
    primary_key = None

    url_base = "https://events.mobilizeamerica.io/api/v1/"

    def __init__(self, org_id: str, **kwargs):
        super().__init__(**kwargs)
        self.page = 1
        self.page_limit = 3

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()

        if response_json.get("next"):
            print(f"CURRENT PAGE: {self.page}")
            next_query_string = urllib.parse.urlsplit(response_json.get("next")).query
            params = dict(urllib.parse.parse_qsl(next_query_string))  # This will return a new param dict by parsing the URL in the 'next' field, e.g. {'page': '2'}
            if self.page < self.page_limit:
                self.page += 1
                return params
            else:
                return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if response_json.get("data"):
            result = [row for row in response_json.get("data") if row['id']>0]
        yield from result

    def path(self, **kwargs) -> str:
        return "organizations"

'''
class Events(HttpStream):
    # Set this as a noop.
    primary_key = None

    url_base = "https://events.mobilizeamerica.io/api/v1/"

    def __init__(self, org_id: str, **kwargs):
        super().__init__(**kwargs)
        self.org_id = org_id
        self.page = 1
        self.page_limit = 3

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()

        if response_json.get("next"):
            next_query_string = urllib.parse.urlsplit(response_json.get("next")).query
            params = dict(urllib.parse.parse_qsl(next_query_string)) #This will return a new param dict by parsing the URL in the 'next' field, e.g. {'page': '2'}
            if self.page < self.page_limit:
                self.page += 1
                return params
            else:
                return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {'org_id': self.org_id, 'cursor': ''} #initialize with blank cursor
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if response_json.get("data"):
            result = [row for row in response_json.get("data") if row['browser_url']] #only include rows where browser_url is not null (should be all valid rows)
        yield from result

    def path(self, **kwargs) -> str:
        return "events"
'''

# Source
class SourceMobilize(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Organizations(org_id=config["org_id"]),
            #Events(org_id=config["org_id"])
        ]
