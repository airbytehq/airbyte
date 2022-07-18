#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.core import Stream


class SubstreamSlicer(StreamSlicer):
    """
    Stream slicer that iterates over the parent's stream slices and records and emits slices by interpolating the slice_definition mapping
    Will populate the state with `parent_stream_slice` and `parent_record` so they can be accessed by other components
    """

    def __init__(
        self,
        parent_streams: List[Stream],
        parent_stream_name_to_slice_key: Mapping[str, str],  # FIXME I think these can also have defaults?
        parent_stream_name_to_stream_slice_key: Mapping[str, str],
    ):
        self._parent_streams = parent_streams
        self._parent_stream_name_to_slice_key = parent_stream_name_to_slice_key
        self._parent_stream_name_to_stream_slice_key = parent_stream_name_to_stream_slice_key  # or "parent_id" FIXME: needs a default!
        self._cursor = None

    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]] = None):
        # FIXME
        print(f"update_cursor. stream_slice: {stream_slice}")

    def request_params(self) -> Mapping[str, Any]:
        # FIXME
        return {}

    def request_headers(self) -> Mapping[str, Any]:
        # FIXME
        return {}

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        # FIXME
        return {}

    def request_body_json(self) -> Optional[Mapping]:
        # FIXME
        return {}

    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        # FIXME
        return {self._stream_state_field: self._cursor} if self._cursor else None

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        """
        Iterate over each parent stream.
        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each records.
        yield a stream slice for each such records.

        If a parent slice contains no record, emit a slice with parent_record=None.

        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name
        """
        if not self._parent_streams:
            yield from []
        else:
            for parent_stream in self._parent_streams:
                parent_field = self._parent_stream_name_to_slice_key[parent_stream.name]
                stream_state_field = self._parent_stream_name_to_stream_slice_key[parent_stream.name]
                for parent_stream_slice in parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
                    empty_parent_slice = True
                    parent_slice = parent_stream_slice.get("slice")

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        empty_parent_slice = False
                        self._cursor = parent_record.get(parent_field)
                        yield {stream_state_field: self._cursor, "parent_slice": parent_slice}
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        self._cursor = parent_stream_slice.get(parent_field)
                        yield {stream_state_field: self._cursor, "parent_slice": parent_slice}
