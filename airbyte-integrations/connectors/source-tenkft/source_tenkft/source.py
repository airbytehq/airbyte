#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Source
class SourceTenkft(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]):
        return TenkftAuthenticator(api_key=config["api_key"])

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            args = self.connector_config(config)
            users = Users(**args).read_records(sync_mode=SyncMode.full_refresh)
            next(users, None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self.connector_config(config)
        return [Users(**args)]

    def connector_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "authenticator": self._get_authenticator(config),
        }


class TenkftAuthenticator(requests.auth.AuthBase):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["auth"] = self.api_key
        return r


# Basic full refresh stream
class TenkftStream(HttpStream):
    @property
    def url_base(self) -> str:
        return "https://api.rm.smartsheet.com"

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class UsersTenkftStream(TenkftStream):
    @property
    def url_base(self) -> str:
        return f"{super().url_base}/api/v1/users?per_page=1000"

    @property
    def http_method(self) -> str:
        return "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class Users(UsersTenkftStream):
    primary_key: Optional[str] = id

    def path(self, **kwargs) -> str:
        return "users"
