#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, Iterable, Mapping, MutableMapping, Optional, Union



from airbyte_cdk.models import SyncMode


from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.stream_slicers import SubstreamSlicer, StreamSlicer, SingleSlice
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import InterpolatedRequestOptionsProvider


@dataclass
# class PosthogIncrementalSlicer(SubstreamSlicer):
class PosthogIncrementalSlicer(SingleSlice):
    options: InitVar[Mapping[str, Any]]
    config: Config
    cursor_field: str
    stream_slice_field = 'project_id'

    def __post_init__(self, options: Mapping[str, Any]):
        self._cursor = {}

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        # This method is called after the records are processed.

        if not last_record:
            self._cursor = stream_slice  # this is actually initial stream state from cli

        project_id = str(stream_slice.get(self.stream_slice_field, ''))
        if project_id:
            current_cursor_value = self._cursor.get(project_id, {}).get('timestamp', '')
            new_cursor_value = last_record.get('timestamp', '')

            self._cursor[project_id] = {'timestamp': max(current_cursor_value, new_cursor_value)}

    def get_stream_state(self):
        return self._cursor

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        """
        Iterate over each parent stream's record and create a StreamSlice for each record.

        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each record.
        yield a stream slice for each such records.

        If a parent slice contains no record, emit a slice with parent_record=None.

        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name
        """
        print(f"components.py stream_slices  stream_state: {stream_state}")
        # print(f"components.py stream_slices  self.state: {self.state}")
        print(f"components.py stream_slices  stream_slices: {[{'project_id': '2331'}]}")
        return [{'project_id': '2331'}]


@dataclass
class PosthogInterpolatedRequestOptionsProvider(InterpolatedRequestOptionsProvider):

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:

        stream_state = stream_state or {}
        stream_slice = stream_slice or {}

        project_id = stream_slice.get('project_id')
        state_value = stream_state.get(project_id, {}).get('timestamp', '')

        params = {"after": state_value or self.config['start_date']}

        print(f"get_request_params !!!!!!!!!!! params: {params}")

        return params
