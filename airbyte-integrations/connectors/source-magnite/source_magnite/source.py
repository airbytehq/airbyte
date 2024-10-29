#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
import json
import time
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from .auth import CookieAuthenticator

class MagniteStream(HttpStream, ABC):
    http_method = "POST"
    def __init__(self, name: str, path: str, primary_key: Union[str, List[str]], data_field: str, **kwargs: Any) -> None:
        self._name = name
        self._path = path
        self._primary_key = primary_key
        self._data_field = data_field
        super().__init__(**kwargs)

    url_base = "https://api.tremorhub.com/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        print("response_json", response_json)
        print("response", list(response_json))
        print(self._data_field)
        if self._data_field:
            result_ready = False
            result_url = f"{self.url_base}{self.path()}/{response_json[self._data_field]}/results"
            while not result_ready:
                result_response = requests.get(result_url, headers=self.authenticator.get_auth_header())
                if result_response.status_code == 200:
                    yield from result_response.json()
                    result_ready = True

                elif result_response.status_code == 202:
                    # print("Results not ready yet. Checking again in 5 seconds.")
                    time.sleep(5)
                else:
                    print(f"Failed to fetch results: {result_response.status_code} - {result_response.text}")
                    break
        else:
            yield from response_json

    @property
    def name(self) -> str:
        return self._name

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return self._path

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key
    
    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        request_payload = {
            "source": "adstats-publisher",
            "fields": [
                "day", "adUnit","publisher","channel","brand", "requests", "impressions", "useRate", "netRevenue", "grossRevenue"
                ],
                "constraints": [
                    {
                        "field": "requests",
                        "operator": ">",
                        "value": 0
                    }
                ],
                "orderings": [
                    {
                        "direction": "asc",
                        "field": "day"
                    }
                ],
                "range": {
                    "range": "lastMonth",  # Define the time range
                    "timeZone": "UTC"
                }
            }
        print(request_payload)
        return request_payload
    

# class Queries(MagniteStream):

#     primary_key = "id"

#     def path(
#             self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
#     ) -> str:
#         return "/v1/resources/queries"

# Source
class SourceMagnite(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:

            auth_headers = CookieAuthenticator(config).get_auth_header()
            url = "https://api.tremorhub.com/v1/resources/queries"
            test_payload = {
                "source": "adstats-publisher",
                "fields": [
                    "day", "adUnit","publisher","channel","brand", "requests", "impressions", "useRate", "netRevenue", "grossRevenue"
                ],
                "constraints": [
                    {
                        "field": "requests",
                        "operator": ">",
                        "value": 0
                    }
                ],
                "orderings": [
                    {
                        "direction": "asc",
                        "field": "day"
                    }
                ],
                "range": {
                    "range": "lastMonth",  # Define the time range
                    "timeZone": "UTC"
                }
            }
            response = requests.request("POST", url=url, headers=auth_headers, data=json.dumps(test_payload))
            response.raise_for_status()
            # TODO: retrieve data???
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = CookieAuthenticator(config)
        return [MagniteStream(name="queries", path="v1/resources/queries", primary_key=None, data_field="code", authenticator=auth)]