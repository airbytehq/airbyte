#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.stream_slicers import SubstreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)


@dataclass
class PosthogIncrementalSlicer(SubstreamSlicer):
    def __post_init__(self, options: Mapping[str, Any]):
        if not self.parent_stream_configs:
            raise ValueError("SubstreamSlicer needs at least 1 parent stream")
        self._cursor = {}
        self._options = options

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        # This method is called after the records are processed.

        if not last_record:
            # this is actually initial stream state from CLI
            self._cursor = stream_slice
            return

        # only one parent stream is expected
        stream_slice_field = self.parent_stream_configs[0].stream_slice_field

        project_id = str(stream_slice.get(stream_slice_field, ""))
        if project_id:
            current_cursor_value = self._cursor.get(project_id, {}).get("timestamp", "")
            new_cursor_value = last_record.get("timestamp", "")

            self._cursor[project_id] = {"timestamp": max(current_cursor_value, new_cursor_value)}


@dataclass
class PosthogInterpolatedRequestOptionsProvider(InterpolatedRequestOptionsProvider):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:

        project_id = str(stream_slice.get("project_id")) if stream_slice else ""
        state_value = stream_state.get(project_id, {}).get("timestamp", "") if stream_state else ""

        return {"after": state_value or self.config["start_date"]}
