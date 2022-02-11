#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class ChartmogulStream(HttpStream, ABC):
    url_base = "https://api.chartmogul.com"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("entries", [])


class Customers(ChartmogulStream):
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        if json_response.get("has_more", False):
            return {"page": json_response.get("current_page") + 1}

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"page": 1 if not next_page_token else next_page_token["page"]}

    def path(self, **kwargs) -> str:
        return "v1/customers"


class Activities(ChartmogulStream):
    primary_key = "uuid"

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        if not json_response.get("has_more", False):
            return None

        return {"start-after": json_response["entries"][-1][self.primary_key]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}

        if next_page_token:
            params.update(next_page_token)
        elif self.start_date:
            params["start-date"] = self.start_date

        return params

    def path(self, **kwargs) -> str:
        return "v1/activities"


class HttpBasicAuthenticator(TokenAuthenticator):
    def __init__(self, token: str, auth_method: str = "Basic", **kwargs):
        auth_string = f"{token}:".encode("utf8")
        b64_encoded = b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)


# Source
class SourceChartmogul(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = HttpBasicAuthenticator(config["api_key"], auth_method="Basic").get_auth_header()
        url = f"{ChartmogulStream.url_base}/v1/ping"
        try:
            resp = requests.get(url, headers=auth)
            resp.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = HttpBasicAuthenticator(config["api_key"], auth_method="Basic")
        return [Customers(authenticator=auth), Activities(authenticator=auth, start_date=config.get("start_date"))]
