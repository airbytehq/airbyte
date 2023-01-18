#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class PartnerstackSlicer(StreamSlicer):
    options: InitVar[Mapping[str, Any]]
    cursor_field: str
    request_cursor_field: str

    def __post_init__(self, options: Mapping[str, Any]):
        self._state = {}

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState, *args, **kwargs) -> Iterable[StreamSlice]:
        yield {self.request_cursor_field: stream_state.get(self.cursor_field, 0)}

    def _max_dt_str(self, *args: str) -> Optional[str]:
        new_state_candidates = list(map(lambda x: int(x), filter(None, args)))
        if not new_state_candidates:
            return
        max_dt = max(new_state_candidates)
        return max_dt

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        slice_state = stream_slice.get(self.cursor_field)
        current_state = self._state.get(self.cursor_field)
        last_cursor = last_record and last_record[self.cursor_field]
        max_dt = self._max_dt_str(slice_state, current_state, last_cursor)
        if not max_dt:
            return
        self._state[self.cursor_field] = max_dt

    def get_stream_state(self) -> StreamState:
        return self._state

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return stream_slice or {}

    def get_request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(self, *args, **kwargs) -> Optional[Union[Mapping, str]]:
        return {}

    def get_request_body_json(self, *args, **kwargs) -> Optional[Mapping]:
        return {}
