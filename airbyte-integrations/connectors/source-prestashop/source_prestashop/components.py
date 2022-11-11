#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
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
