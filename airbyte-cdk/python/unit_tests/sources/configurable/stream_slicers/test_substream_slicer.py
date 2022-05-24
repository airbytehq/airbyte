#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.configurable.states.dict_state import DictState
from airbyte_cdk.sources.configurable.stream_slicers.substream_slicer import SubstreamSlicer
from airbyte_cdk.sources.streams.core import Stream


class MockStream(Stream):
    first_slice = [{"id": 0, "slice": "first", "data": "A"}, {"id": 1, "slice": "first", "data": "B"}]
    second_slice = [{"id": 2, "slice": "second", "data": "C"}]

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{"slice": "first"}, {"slice": "second"}, {"slice": "third"}]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            yield from self.first_slice + self.second_slice
        elif stream_slice.get("slice") == "first":
            yield from self.first_slice
        elif stream_slice.get("slice") == "second":
            yield from self.second_slice
        elif stream_slice.get("slice") == "third":
            yield from []
        else:
            yield from self.first_slice + self.second_slice


def test():
    parent_stream = MockStream()
    state = DictState()
    parent_id = "{{ parent_record['id'] }}"
    slicer = SubstreamSlicer(parent_stream, state, parent_id)
    stream_slices = [s for s in slicer.stream_slices(SyncMode.incremental, None)]
    print(f"actual_slices:\n{stream_slices}")
    # FIXME: need to figure out how to convert the parent_id back to a number...
    assert stream_slices == [
        {"slice": "first", "parent_id": "0"},
        {"slice": "first", "parent_id": "1"},
        {"slice": "second", "parent_id": "2"},
        {"slice": "third", "parent_id": None},
    ]
