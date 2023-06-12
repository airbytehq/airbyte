#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import PerPartitionStreamSlice
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class MigratingPerPartitionCursor(StreamSlicer):
    """
    The goal of MigratingPerPartitionCursor is not handle a timely migration from flat state to per partition state. Flat states look like:
    ```
    {
      <cursor_field>: <cursor_value>,
      <partition_field>: <partition_value>
    }
    ```

    However, per partition states look like:
    ```
    {
      "states": [
        {
          <partition_field>: <partition_value>,
          <cursor_field>: <cursor_value>
        }
    ...
    ]}
    ```

    Once all connections are executed at least once using this class, the state should be using the new format and this class isn't
    necessary anymore.
    """

    _NO_STATE = {}
    _NO_CURSOR_STATE = {}
    _KEY = 0
    _VALUE = 1

    def __init__(self, decorated):
        self._decorated = decorated

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[PerPartitionStreamSlice]:
        return self._decorated.stream_slices(sync_mode, stream_state)

    def update_cursor(self, stream_slice: PerPartitionStreamSlice, last_record: Optional[Record] = None):
        if not last_record and self._requires_migration(stream_slice):
            # The `update_cursor` method is called without `last_record` in order to set the initial state. In that case, stream_slice is
            # not a PerPartitionStreamSlice but is a dict representing the state
            self._decorated.set_default_state(stream_slice)
        else:
            self._decorated.update_cursor(stream_slice, last_record)

    def get_stream_state(self) -> StreamState:
        return self._decorated.get_stream_state()

    def select(
        self, stream_slice: Optional[PerPartitionStreamSlice] = None, stream_state: Optional[StreamState] = None
    ) -> Optional[StreamState]:
        if not stream_state:
            return self._decorated.select(stream_slice, stream_state)
        elif self._requires_migration(stream_state):
            return stream_state
        return self._decorated.select(stream_slice, stream_state)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def _requires_migration(self, stream_state: StreamState) -> bool:
        return stream_state and "states" not in stream_state
