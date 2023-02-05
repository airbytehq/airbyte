#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


@dataclass
class TwilioCartesianProductStreamSlicer(CartesianProductStreamSlicer):
    def __post_init__(self, options: Mapping[str, Any]):
        self._cursor = {}
        self._options = options

    def get_stream_state(self) -> Mapping[str, Any]:
        return self._cursor

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        record_slicer, datetime_slicer = self.stream_slicers
        for record_slice in record_slicer.stream_slices(sync_mode, stream_state):
            record_id = record_slice["record"]["sid"]
            datetime_slicer._cursor = None
            for datetime_slice in datetime_slicer.stream_slices(sync_mode, stream_state.get(record_id)):
                yield record_slice | datetime_slice

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        datetime_slicer = self.stream_slicers[1]
        datetime_slicer.update_cursor(stream_slice, last_record)
        if last_record:
            record_id = stream_slice["record"]["sid"]
            self._cursor.setdefault(record_id, {}).update(datetime_slicer.get_stream_state())
        else:
            self._cursor = stream_slice
