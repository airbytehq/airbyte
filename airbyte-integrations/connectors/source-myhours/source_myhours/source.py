#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .constants import request_headers, url_base


class MyhoursStream(HttpStream, ABC):
    url_base = url_base + "/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json = response.json()
        for record in json:
            yield record

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return request_headers


class Clients(MyhoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Clients"


class Projects(MyhoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Projects/getAll"


class Tags(MyhoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Tags"


class TimeLogs(MyhoursStream):
    primary_key = "logId"

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        start_date: str,
        batch_size: int,
        **kwargs,
    ):
        self.start_date = pendulum.parse(start_date)
        self.batch_size = batch_size

        if self.start_date > pendulum.now():
            self.logger.log(logging.WARN, f'Stream {self.name}: start_date "{start_date.isoformat()}" should be before today.')

        super().__init__(authenticator=authenticator)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Reports/activity"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        previous_query = parse_qs(urlparse(response.request.url).query)
        previous_end = pendulum.parse(previous_query["DateTo"][0])

        new_from = previous_end.add(days=1)
        new_to = new_from.add(days=self.batch_size - 1)

        if new_from > pendulum.now():
            return None

        return {
            "DateFrom": new_from.to_date_string(),
            "DateTo": new_to.to_date_string(),
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        if next_page_token is None:
            return {"DateFrom": self.start_date.to_date_string(), "DateTo": self.start_date.add(days=6).to_date_string()}
        return next_page_token


class Users(MyhoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Users/getAll"


# Source
class SourceMyhours(AbstractSource):
    def get_access_token(self, config) -> Tuple[str, any]:
        email = config["email"]
        password = config["password"]
        url = f"{url_base}/tokens/login"

        try:
            payload = json.dumps({"grantType": "password", "email": email, "password": password, "clientId": "api"})
            response = requests.post(url, headers=request_headers, data=payload)
            response.raise_for_status()
            json_response = response.json()
            return json_response.get("accessToken", None), None if json_response is not None else None, None
        except requests.exceptions.RequestException as e:
            return None, e

    def check_connection(self, logger: AirbyteLogger, config) -> Tuple[bool, any]:
        access_token = self.get_access_token(config)
        url = f"{url_base}/Clients"
        token_value = access_token[0]
        token_exception = access_token[1]

        if token_exception:
            return False, token_exception

        if token_value:
            headers = TokenAuthenticator(token=token_value).get_auth_header()
            headers.update(request_headers)
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return True, None
            except requests.exceptions.RequestException as e:
                return False, e
        return False, "Token not found"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        access_token = self.get_access_token(config)

        auth = TokenAuthenticator(token=access_token[0])
        return [
            Clients(authenticator=auth),
            Projects(authenticator=auth),
            Tags(authenticator=auth),
            TimeLogs(authenticator=auth, start_date=config["start_date"], batch_size=config["logs_batch_size"]),
            Users(authenticator=auth),
        ]
