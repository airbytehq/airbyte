#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

class FlexportError(Exception):
    pass

class FlexportStream(HttpStream, ABC):
    url_base = "https://api.flexport.com/"
    raise_on_http_errors = False
    page_size = 500

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # https://apidocs.flexport.com/reference/pagination
        # All list endpoints return paginated responses. The response object contains
        # elements of the current page, and links to the previous and next pages.
        data = response.json()["data"]

        if data["next"]:
            url = urlparse(data["next"])
            qs = dict(parse_qsl(url.query))

            return {
                "page": qs["page"],
                "per": qs["per"],
            }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return next_page_token

        return {
            "page": 1,
            "per": self.page_size,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # https://apidocs.flexport.com/reference/response-layout
        json = response.json()

        http_error = None
        try:
            response.raise_for_status()
        except Exception as exc:
            http_error = exc

        error = json.get("error")
        if error:
            raise FlexportError(f"{error['code']}: {error['message']}") from http_error
        elif http_error:
            raise http_error

        yield from json["data"]["data"]


class Companies(FlexportStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "network/companies"


class Locations(FlexportStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "network/locations"


class Products(FlexportStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "products"


class SourceFlexport(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = {"Authorization": f"Bearer {config['api_key']}"}
        response = requests.get(f"{FlexportStream.url_base}network/companies?page=1&per=1", headers=headers)

        try:
            response.raise_for_status()
        except Exception as exc:
            try:
                error = response.json()["errors"][0]
                if error:
                    return False, FlexportError(f"{error['code']}: {error['message']}")
                return False, exc
            except Exception:
                return False, exc

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_key"])
        return [
            Companies(authenticator=auth),
            Locations(authenticator=auth),
            Products(authenticator=auth),
        ]
