#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.states.dict_state import DictState
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.core import Stream


class SubstreamSlicer(StreamSlicer):
    """
    Stream slicer that iterates over the parent's stream slices and records and emits slices by interpolating the slice_definition mapping
    Will populate the state with `parent_stream_slice` and `parent_record` so they can be accessed by other components
    """

    def __init__(self, parent_streams: List[Stream], state: DictState, slice_definition: Mapping[str, Any]):
        self._parent_streams = parent_streams
        self._state = state
        self._interpolation = JinjaInterpolation()
        self._slice_definition = slice_definition

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        if not self._parent_streams:
            yield from []
        else:
            for parent_stream in self._parent_streams:
                for parent_stream_slice in parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
                    self._state.update_state(parent_stream_slice=parent_stream_slice)
                    self._state.update_state(parent_record=None)
                    empty_parent_slice = True

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        empty_parent_slice = False
                        slice_definition = {
                            self._interpolation.eval(
                                k,
                                None,
                                None,
                                parent_stream_slice=parent_stream_slice,
                                parent_record=parent_record,
                                parent_stream_name=parent_stream.name,
                            ): self._interpolation.eval(
                                v,
                                None,
                                None,
                                parent_stream_slice=parent_stream_slice,
                                parent_record=parent_record,
                                parent_stream_name=parent_stream.name,
                            )
                            for k, v in self._slice_definition.items()
                        }
                        self._state.update_state(parent_record=parent_record)
                        yield slice_definition
                    # If the parent slice contains no records,
                    # yield a slice definition with parent_record==None
                    if empty_parent_slice:
                        slice_definition = {
                            self._interpolation.eval(
                                k,
                                None,
                                None,
                                parent_stream_slice=parent_stream_slice,
                                parent_record=None,
                                parent_stream_name=parent_stream.name,
                            ): self._interpolation.eval(
                                v,
                                None,
                                None,
                                parent_stream_slice=parent_stream_slice,
                                parent_record=None,
                                parent_stream_name=parent_stream.name,
                            )
                            for k, v in self._slice_definition.items()
                        }
                        print(f"slice_definition: {slice_definition}")
                        yield slice_definition
