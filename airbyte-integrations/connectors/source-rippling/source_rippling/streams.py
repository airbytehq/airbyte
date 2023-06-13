#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class RipplingStream(HttpStream, ABC):
    @property
    def url_base(self) -> str:
        return "https://api.rippling.com/platform/api/"

    offset = 0
    limit = 50

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if len(response_data) == self.limit:
            self.offset = self.offset + self.limit
            return {"offset": self.offset, "limit": self.limit}
        return {}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return next_page_token if next_page_token else {"limit": self.limit, "offset": self.offset}  # type:ignore

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Employees(RipplingStream):
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def __init__(self, filters, **kwargs):
        super().__init__(**kwargs)
        self.filters = [filter_.strip() for filter_ in filters.split(",")] if filters else []

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema = super().get_json_schema()
        json_schema["properties"] = {k: v for k, v in json_schema["properties"].items() if k not in self.filters}
        return json_schema

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "employees/include_terminated"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from [{k: v for k, v in employee.items() if k not in self.filters} for employee in response.json()]


class LeaveRequests(RipplingStream):
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "leave_requests"

    def stream_slices(self, **kwargs):
        employees_stream = Employees(authenticator=self._session.auth, filters="")
        for employee in employees_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"employee_id": employee["id"]}  # type: ignore

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {"role": stream_slice["employee_id"]}  # type: ignore

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class LeaveBalances(RipplingStream):
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "role"

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "leave_balances"


class CompanyLeaveTypes(RipplingStream):
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "company_leave_types"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if len(response_data) == self.limit:
            self.offset = self.offset + self.limit
            return {"offset": self.offset, "limit": self.limit}
        return None
