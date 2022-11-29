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
        date_shortcut = {"date_shortcut": "custom"}  # required request param when specified date_from and date_to params
        params.update(date_shortcut)
        return params


@dataclass
class ZenloopSubstreamSlicer(SubstreamSlicer):
    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        """

        config_parent_field : parent field name in config

        Use parent id's as stream state value if it specified in config or
        create stream_slices according SubstreamSlicer logic.

        """
        config = self._options.get("config")
        parent_field = self._options.get("config_parent_field")
        custom_stream_state_value = config.get(parent_field)

        if not custom_stream_state_value:
            yield from super().stream_slices(sync_mode, stream_state)
        else:
            for parent_stream_config in self.parent_stream_configs:
                stream_state_field = parent_stream_config.stream_slice_field or None
                yield {stream_state_field: custom_stream_state_value, "parent_slice": {}}
