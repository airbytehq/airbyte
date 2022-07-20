#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.streams.core import Stream


@dataclass
class ParentStreamConfig:
    stream: Stream
    slice_key: str
    stream_slice_field: str
    request_option: Optional[RequestOption] = None


class SubstreamSlicer(StreamSlicer):
    """
    Stream slicer that iterates over the parent's stream slices and records and emits slices by interpolating the slice_definition mapping
    Will populate the state with `parent_stream_slice` and `parent_record` so they can be accessed by other components
    """

    def __init__(
        self,
        parent_streams_configs: List[ParentStreamConfig],
    ):
        self._parent_stream_configs = parent_streams_configs
        self._cursor = None

    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]] = None):
        cursor = {}
        for parent_stream_config in self._parent_stream_configs:
            slice_value = stream_slice.get(parent_stream_config.stream_slice_field)
            if slice_value:
                cursor.update({parent_stream_config.stream_slice_field: slice_value})
        self._cursor = cursor

    def request_params(self) -> Mapping[str, Any]:
        return self._get_request_option(RequestOptionType.request_parameter)

    def request_headers(self) -> Mapping[str, Any]:
        return self._get_request_option(RequestOptionType.header)

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return self._get_request_option(RequestOptionType.body_data)

    def request_body_json(self) -> Optional[Mapping]:
        return self._get_request_option(RequestOptionType.body_json)

    def _get_request_option(self, option_type: RequestOptionType):
        params = {}
        for parent_config in self._parent_stream_configs:
            if parent_config.request_option and parent_config.request_option.inject_into == option_type:
                key = parent_config.stream_slice_field
                value = self._cursor.get(key)
                if value:
                    params.update({key: value})
        return params

    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        return self._cursor if self._cursor else None

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
        if not self._parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self._parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.slice_key
                stream_state_field = parent_stream_config.stream_slice_field
                for parent_stream_slice in parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
                    empty_parent_slice = True
                    parent_slice = parent_stream_slice.get("slice")

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        empty_parent_slice = False
                        stream_state_value = parent_record.get(parent_field)
                        yield {stream_state_field: stream_state_value, "parent_slice": parent_slice}
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        stream_state_value = parent_stream_slice.get(parent_field)
                        yield {stream_state_field: stream_state_value, "parent_slice": parent_slice}
