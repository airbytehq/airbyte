#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.states.dict_state import DictState
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


class SubstreamSlicer(StreamSlicer):
    def __init__(self, parent_stream, state: DictState, slice_definition: Mapping[str, Any], **kwargs):
        self._parent_stream = parent_stream
        self._state = state
        self._interpolation = JinjaInterpolation()
        self._slice_definition = slice_definition

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        for parent_stream_slice in self._parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
            self._state.update_state(parent_stream_slice=parent_stream_slice)
            self._state.update_state(parent_record=None)
            empty = True

            for parent_record in self._parent_stream.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
            ):
                empty = False
                slice_definition = {
                    k: self._interpolation.eval(v, None, None, parent_record=parent_record) for k, v in self._slice_definition.items()
                }
                self._state.update_state(parent_record=parent_record)
                yield {**parent_stream_slice, **slice_definition}
            if empty:
                yield {**parent_stream_slice, **{k: None for k, v in self._slice_definition.items()}}
