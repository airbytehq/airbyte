#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import math
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import SubstreamSlicer
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class ZenloopDatetimeStreamSlicer(DatetimeStreamSlicer):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        params = super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        date_shortcut = {"date_shortcut": "custom"}
        params.update(date_shortcut)
        return params


@dataclass
class ZenloopSubstreamSlicer(SubstreamSlicer):
    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        config = self._options.get("config")
        parent_field = self._options.get("config_parent_field")
        custom_stream_state_value = config.get(parent_field)

        if not custom_stream_state_value:
            yield from super().stream_slices(sync_mode, stream_state)
        else:
            for parent_stream_config in self.parent_stream_configs:
                stream_state_field = parent_stream_config.stream_slice_field or None
                yield {stream_state_field: custom_stream_state_value, "parent_slice": {}}


@dataclass
class ZenloopPageIncrement(PageIncrement):
    """
    Starts page from 1 instead of the default value that is 0. Stops Pagination when next page not exist.
    """

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = response.json()

        current_page = decoded_response["meta"]["page"]
        per_page = decoded_response["meta"]["per_page"]
        total = decoded_response["meta"]["total"]

        next_page_exist = current_page < math.ceil(total / per_page)

        if next_page_exist:
            self._page += 1
            return self._page
        else:
            return None

    def __post_init__(self, options: Mapping[str, Any]):
        self._page = 1

    def reset(self):
        self._page = 1
