#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import functools
import requests
from abc import ABC
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from datetime import datetime
from enum import Enum
from prance import ResolvingParser
from requests.auth import AuthBase
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

API_VERSION = "3.1"


class LookerException(Exception):
    pass


class LookerStream(HttpStream, ABC):

    def __init__(self, *, domain: str, **kwargs):
        self._domain = domain
        super().__init__(**kwargs)

    @property
    def url_base(self):
        return f"https://{self._domain}/api/{API_VERSION}/"

    primary_key = None


class SwaggerParser(LookerStream):
    primary_key = None

    class Endpoint:
        def __init__(self, *, path: str, schema: Mapping[str, Any], operation_id: str, summary: str):
            self.path, self.schema, self.operation_id, self.summary = path, schema, operation_id, summary

    def path(self, **kwargs: Any):
        return "swagger.json"

    def next_page_token(self, **kwargs) -> Optional[Mapping[str, Any]]:
        return None

    @functools.lru_cache(maxsize=None)
    def get_endpoints(self):
        parser = next(self.read_records(sync_mode=None))
        endpoints = []
        for path, methods in parser.specification["paths"].items():
            if not methods.get("get") or not methods["get"]["responses"].get("200"):
                continue
            get_data = methods["get"]
            endpoints.append(self.Endpoint(path=path, schema=get_data["responses"]["200"],
                                           summary=get_data["summary"], operation_id=get_data["operationId"]))
        return endpoints

    def parse_response(self, response: requests.Response, **kwargs: Any) -> Iterable[Mapping]:
        yield ResolvingParser(spec_string=response.text)


class LookerStream2(LookerStream, ABC):
    def __init__(self, *, swagger_parser: SwaggerParser, run_look_ids: List[str], **kwargs):
        self._run_look_ids = [int(id) for id in run_look_ids if id]
        self._swagger_parser = swagger_parser
        super().__init__(**kwargs)
        self._swagger_parser.get_endpoints()

    def path(self, **kwargs: Any):
        return "swagger.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Abstract method of HttpStream - should be overwritten.
        Returning None means there are no more pages to read in response.
        """
        raise Exceptio
        next_page = response.json().get("pages", {}).get("next")

        if next_page:
            return dict(parse_qsl(urlparse(next_page).query))

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            error_message = e.response.text
            if error_message:
                self.logger.error(f"Stream {self.name}: {e.response.status_code} " f"{e.response.reason} - {error_message}")
            raise e

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:

        data = response.json()

        for data_field in self.data_fields:
            if data_field not in data:
                continue
            data = data[data_field]
            if data and isinstance(data, list):
                break

        if isinstance(data, dict):
            yield data
        else:
            yield from data
