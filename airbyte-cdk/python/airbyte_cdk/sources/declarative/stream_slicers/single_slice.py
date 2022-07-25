#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class SingleSlice(StreamSlicer):
    """Stream slicer returning only a single stream slice"""

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        pass

    def get_stream_state(self) -> StreamState:
        return {}

    def request_params(self) -> Mapping[str, Any]:
        return {}

    def request_headers(self) -> Mapping[str, Any]:
        return {}

    def request_body_data(self) -> Mapping[str, Any]:
        return {}

    def request_body_json(self) -> Mapping[str, Any]:
        return {}

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[StreamSlice]:
        return [dict()]

    def request_kwargs(self) -> Mapping[str, Any]:
        # Never update kwargs
        return {}
