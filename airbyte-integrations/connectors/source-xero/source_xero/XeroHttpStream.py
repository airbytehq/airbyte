from abc import ABC
from typing import Any, Iterable, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from urllib.parse import urljoin

from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException


class XeroHttpStream(HttpStream, ABC):
    url_base = "http://abilling01.prod.dld"
    xero_id = ""
    BODY_REQUEST_METHODS = ("POST", "PUT", "PATCH", "GET")
    dolead_id = "ed4cac23-e9fe-4e05-89d6-b5c9fc6d2a32"
    dolead_inc_id = "c1de2758-b8aa-45d7-8c01-163c3bbf8c39"
    dolead_uk_id = "bfa6caee-df20-41f8-a42b-8b73603159d7"
    dolead_dds_id = "8cfa6be1-0d88-4046-b9d4-e5055b0ade76"

    # Set this as a noop.
    primary_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for backoff policy.
        """
        return 40

    def path(self, **kwargs) -> str:
        return ""

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        decoded_response = response.json()
        if decoded_response.get("data") != []:
            last_object_page = decoded_response.get("page")
            return int(last_object_page) + 1
        else:
            return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def _create_prepared_request(
            self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None, data: Any = None
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": urljoin(self.url_base, path), "headers": headers, "params": params}
        if self.http_method.upper() in self.BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return response.json()
