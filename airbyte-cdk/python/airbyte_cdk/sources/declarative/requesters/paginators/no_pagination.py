#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class NoPagination(Paginator, JsonSchemaMixin):
    """
    Pagination implementation that never returns a next page.
    """

    options: InitVar[Mapping[str, Any]]

    def path(self) -> Optional[str]:
        return None

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return {}

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return {}

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Mapping[str, Any]:
        return {}

    def reset(self):
        # No state to reset
        pass
