#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class SingleSlice(StreamSlicer):
    """Stream slicer returning only a single stream slice"""

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        pass

    def get_stream_state(self) -> Optional[StreamState]:
        return None

    def request_params(self) -> Mapping[str, Any]:
        return {}

    def request_headers(self) -> Mapping[str, Any]:
        return {}

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return {}

    def request_body_json(self) -> Optional[Mapping]:
        return {}

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[StreamSlice]:
        return [dict()]
