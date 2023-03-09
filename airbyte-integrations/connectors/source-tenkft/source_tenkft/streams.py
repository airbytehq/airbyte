#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class TenkftStream(HttpStream, ABC):
    """
    Tenkft API Reference: https://10kft.github.io/10kft-api
    """

    primary_key: Optional[str] = id
    parse_response_root: Optional[str] = None

    def __init__(self, start_date: str, end_date: str, query: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.query = query
        self._cursor_value = None

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
        params = {"per_page": 1000}
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


class IncrementalTenkftStream(TenkftStream, IncrementalMixin, ABC):
    primary_key: Optional[str] = "id"
    parse_response_root: Optional[str] = None

    def __init__(self, start_date: str, end_date: str, query: str, **kwargs):
        super().__init__(start_date, end_date, query, **kwargs)
        self._cursor_value = ""

    @property
    def url_base(self) -> str:
        return f"{super().url_base}/api/v1/"

    @property
    def http_method(self) -> str:
        return "GET"

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "updated_at"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        cursor = response_json.get("updated_at", {})
        if not cursor:
            self._cursor_value = self.end_date
        else:
            return self.get_payload(cursor)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record[self.cursor_field] = self._cursor_value if self._cursor_value else self.end_date
        return record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if self.start_date >= self.end_date or self.end_date <= self._cursor_value:
            return []
        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def get_payload(self, cursor: Optional[str]) -> Mapping[str, Any]:
        payload = {
            "filter": {"query": self.query, "from": self._cursor_value if self._cursor_value else self.start_date, "to": self.end_date},
            "page": {"limit": 1000},
        }
        if cursor:
            payload["page"]["cursor"] = cursor

        return payload


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


class BillRates(IncrementalTenkftStream):
    """
    API docs: https://10kft.github.io/10kft-api/#bill-rates
    """

    name = "bill_rates"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        project_id = stream_slice["project_id"]
        return f"projects/{project_id}/bill_rates"
