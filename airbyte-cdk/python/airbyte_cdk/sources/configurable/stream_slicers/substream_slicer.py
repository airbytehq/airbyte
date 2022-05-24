#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.configurable.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.configurable.states.dict_state import DictState
from airbyte_cdk.sources.configurable.stream_slicers.stream_slicer import StreamSlicer


class SubstreamSlicer(StreamSlicer):
    def __init__(self, parent_stream, state: DictState, parent_id, **kwargs):
        self._parent_stream = parent_stream
        self._state = state
        self._interpolation = JinjaInterpolation()
        self._parent_id = parent_id

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        for parent_stream_slice in self._parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
            self._state.update_state(parent_stream_slice=parent_stream_slice)
            for parent_record in self._parent_stream.read_records(sync_mode=SyncMode.full_refresh):
                parent_id = self._interpolation.eval(self._parent_id, None, None, parent_record=parent_record)
                yield {**parent_stream_slice, **{"parent_id": parent_id}}
