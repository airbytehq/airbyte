#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
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
        return [Users(**args), Projects(**args), ProjectAssignments(**args), BillRates(**args)]

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
class TenkftStream(HttpStream, ABC):
    primary_key: Optional[str] = id
    parse_response_root: Optional[str] = None

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
        params = {"per_page": 100}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield response_json


class ApiTenkftStream(TenkftStream, ABC):
    @property
    def url_base(self) -> str:
        return f"{super().url_base}/api/v1/"

    @property
    def http_method(self) -> str:
        return "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class Users(ApiTenkftStream):
    """
    API docs: https://10kft.github.io/10kft-api/#users
    """

    def path(self, **kwargs) -> str:
        return "users"


class Projects(ApiTenkftStream):
    """
    API docs: https://10kft.github.io/10kft-api/#list-projects
    """

    def path(self, **kwargs) -> str:
        return "projects"


class ProjectAssignments(ApiTenkftStream):
    """
    API docs: https://10kft.github.io/10kft-api/#list-all-assignments
    """

    name = "project_assignments"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        project_id = stream_slice["project_id"]
        return f"projects/{project_id}/assignments"


class BillRates(ApiTenkftStream):
    """
    API docs: https://10kft.github.io/10kft-api/#bill-rates
    """

    name = "bill_rates"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        project_id = stream_slice["project_id"]
        return f"projects/{project_id}/bill_rates"
