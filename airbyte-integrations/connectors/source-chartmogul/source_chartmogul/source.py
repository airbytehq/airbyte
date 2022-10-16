#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from base64 import b64encode
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException


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


class CustomerCount(ChartmogulStream):
    primary_key = "date"

    def __init__(self, start_date: str, interval: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        self.interval = interval

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return {
            "start-date": self.start_date,
            "end-date": self.end_date,
            "interval": self.interval,
        }

    def _create_prepared_request(
        self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None, data: Any = None
    ) -> requests.PreparedRequest:
        """
        Override to make possible sending http body with GET request.
        """
        args = {"method": self.http_method, "url": urljoin(self.url_base, path), "headers": headers, "params": params}
        if json and data:
            raise RequestBodyException(
                "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
            )
        elif json:
            args["json"] = json
        elif data:
            args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def path(self, **kwargs) -> str:
        return "v1/metrics/customer-count"


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
        return [
            Customers(authenticator=auth),
            CustomerCount(authenticator=auth, start_date=config.get("start_date"), interval=config.get("interval")),
            Activities(authenticator=auth, start_date=config.get("start_date")),
        ]
