#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import base64


# Basic full refresh stream
class WinningtempStream(HttpStream, ABC):
    url_base = "https://api.winningtemp.com"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__()
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')

        self.access_token = None
        self.generate_access_token()

    def generate_access_token(self):
        # url = "https://api.winningtemp.com/auth"

        encoded_str = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii")).decode("utf-8")
        headers = {"accept": "application/json", "Authorization": f"Basic {encoded_str}"}
        response = requests.post(f"{self.url_base}/auth", headers=headers)

        self.access_token = response.json().get("access_token", "")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"accept": "application/json", "authorization": f"Bearer {self.access_token}"}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class SegmentationGroups(WinningtempStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "segmentation/v1/groups"


class SurveyCategories(WinningtempStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "survey/v1/Categories"


class SurveyQuestions(WinningtempStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "survey/v1/Questions"


# Source
class SourceWinningtemp(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        return [SegmentationGroups(config=config), SurveyCategories(config=config), SurveyQuestions(config=config)]
