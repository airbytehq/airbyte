#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth

# Basic full refresh stream


class PersistiqStream(HttpStream, ABC):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    url_base = "https://api.persistiq.com/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        if not json_response.get("has_more", False):
            return None

        return {"page": json_response.get("next_page")[-1]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"page": 1 if not next_page_token else next_page_token["page"]}

    def request_headers(self, **kwargs) -> MutableMapping[str, Any]:
        return {"x-api-key": self.api_key}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Users(PersistiqStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json = response.json()
        yield from json["users"]


class Leads(PersistiqStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "leads"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json = response.json()
        yield from json["leads"]


class Campaigns(PersistiqStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "campaigns"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json = response.json()
        yield from json["campaigns"]


# Source


class SourcePersistiq(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = {"x-api-key": config["api_key"]}
        url = "https://api.persistiq.com/v1/users"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [
            Users(authenticator=auth, api_key=config["api_key"]),
            Leads(authenticator=auth, api_key=config["api_key"]),
            Campaigns(authenticator=auth, api_key=config["api_key"]),
        ]
