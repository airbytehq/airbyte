#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class CopperStream(HttpStream, ABC):
    def __init__(self, *args, api_key: str = None, user_email: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_email = user_email
        self._api_key = api_key

    url_base = "https://api.copper.com/developer_api/v1/"

    @property
    def http_method(self) -> str:
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        body = json.loads(response.request.body)
        result = response.json()
        if body and result:
            page_number = body.get("page_number")
            return {"page_number": page_number + 1, "page_size": 200}
        else:
            return None

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:

        if next_page_token:
            return next_page_token

        return {"page_number": 1, "page_size": 200}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "X-PW-AccessToken": self._api_key,
            "X-PW-UserEmail": self._user_email,
            "X-PW-Application": "developer_api",
            "Content-type": "application/json",
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_result = response.json()
        if response_result:
            yield from response_result
        return


class People(CopperStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "people/search"


class Projects(CopperStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "projects/search"


class Companies(CopperStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "companies/search"


# Source
class SourceCopper(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            records = People(**config).read_records(sync_mode=SyncMode.full_refresh)
            next(records, None)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Copper API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [People(**config), Companies(**config), Projects(**config)]
