#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar, Iterable, List, Mapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class LimitOffsetPaginator(Paginator, JsonSchemaMixin):

    limit_offset_option: RequestOption
    pagination_strategy: PaginationStrategy
    options: InitVar[Mapping[str, Any]]
    _token: Optional[Any] = field(init=False, repr=False, default=None)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        self._token = self.pagination_strategy.next_page_token(response, last_records)
        if self._token:
            return {"next_page_token": self._token}
        else:
            return None

    def path(self) -> Optional[str]:
        return None

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        page_size = self.pagination_strategy.get_page_size()
        if self._token:
            return {self.limit_offset_option.field_name: f"{self._token},{page_size}"}
        return {self.limit_offset_option.field_name: str(page_size)}

    def get_request_headers(self, **kwargs) -> Mapping[str, str]:
        return {}

    def get_request_body_data(self, **kwargs) -> Mapping[str, Any]:
        return {}

    def get_request_body_json(self, **kwargs) -> Mapping[str, Any]:
        return {}

    def reset(self):
        self.pagination_strategy.reset()


@dataclass
class NoSlicer(StreamSlicer, JsonSchemaMixin):

    options: InitVar[Mapping[str, Any]]
    config: Config
    cursor_field: Union[InterpolatedString, str]
    primary_key: Union[InterpolatedString, str]
    _cursor: Optional[datetime.datetime] = field(repr=False, default=None)
    _cursor_end: datetime.datetime = field(repr=False, default_factory=datetime.datetime.utcnow)
    _filter_params: bool = field(repr=False, default=False)

    DATETIME_FORMAT: ClassVar[str] = "%Y-%m-%d %H:%M:%S"

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field.eval(self.config): self._cursor.strftime(self.DATETIME_FORMAT)} if self._cursor else {}

    @staticmethod
    def safe_max(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return max(a, b)

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        cursor_field = self.cursor_field.eval(self.config)
        self._cursor = stream_slice.get(cursor_field)
        if self._cursor:
            self._cursor = datetime.datetime.strptime(self._cursor, self.DATETIME_FORMAT)
        if last_record:
            self._cursor = self.safe_max(datetime.datetime.strptime(last_record[cursor_field], self.DATETIME_FORMAT), self._cursor)

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        if self._cursor:
            self._filter_params = True
        yield self.get_stream_state()

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        cursor_field = self.cursor_field.eval(self.config)
        primary_key = self.primary_key.eval(self.config)
        params = {
            "date": "1",
            "sort": f"[{cursor_field}_ASC,{primary_key}_ASC]",
        }
        if self._filter_params:
            start_datetime = self._cursor.strftime(self.DATETIME_FORMAT)
            end_datetime = self._cursor_end.strftime(self.DATETIME_FORMAT)
            params[f"filter[{cursor_field}]"] = f"[{start_datetime},{end_datetime}]"
        return params

    def get_request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(self, **kwargs) -> Mapping[str, Any]:
        return {}

    def get_request_body_json(self, **kwargs) -> Mapping[str, Any]:
        return {}
