#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional, Union

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class ParentStreamConfig(JsonSchemaMixin):
    """
    Describes how to create a stream slice from a parent stream

    stream: The stream to read records from
    parent_key: The key of the parent stream's records that will be the stream slice key
    stream_slice_field: The stream slice key
    request_option: How to inject the slice value on an outgoing HTTP request
    """

    stream: Stream
    parent_key: Union[InterpolatedString, str]
    stream_slice_field: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    request_option: Optional[RequestOption] = None

    def __post_init__(self, options: Mapping[str, Any]):
        self.parent_key = InterpolatedString.create(self.parent_key, options=options)
        self.stream_slice_field = InterpolatedString.create(self.stream_slice_field, options=options)


@dataclass
class SubstreamSlicer(StreamSlicer, JsonSchemaMixin):
    """
    Stream slicer that iterates over the parent's stream slices and records and emits slices by interpolating the slice_definition mapping
    Will populate the state with `parent_stream_slice` and `parent_record` so they can be accessed by other components

    Attributes:
        parent_stream_configs (List[ParentStreamConfig]): parent streams to iterate over and their config
    """

    parent_stream_configs: List[ParentStreamConfig]
    config: Config
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        if not self.parent_stream_configs:
            raise ValueError("SubstreamSlicer needs at least 1 parent stream")
        self._cursor = None
        self._options = options

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        # This method is called after the records are processed.
        cursor = {}
        for parent_stream_config in self.parent_stream_configs:
            stream_slice_field = parent_stream_config.stream_slice_field.eval(self.config)
            slice_value = stream_slice.get(stream_slice_field)
            if slice_value:
                cursor.update({stream_slice_field: slice_value})
        self._cursor = cursor

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        params = {}
        if stream_slice:
            for parent_config in self.parent_stream_configs:
                if parent_config.request_option and parent_config.request_option.inject_into == option_type:
                    key = parent_config.stream_slice_field.eval(self.config)
                    value = stream_slice.get(key)
                    if value:
                        params.update({key: value})
        return params

    def get_stream_state(self) -> StreamState:
        return self._cursor if self._cursor else {}

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
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key.eval(self.config)
                stream_state_field = parent_stream_config.stream_slice_field.eval(self.config)
                for parent_stream_slice in parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
                    empty_parent_slice = True
                    parent_slice = parent_stream_slice

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        # Skip non-records (eg AirbyteLogMessage)
                        if isinstance(parent_record, AirbyteMessage):
                            if parent_record.type == Type.RECORD:
                                parent_record = parent_record.record.data
                            else:
                                continue

                        try:
                            stream_state_value = dpath.util.get(parent_record, parent_field)
                        except KeyError:
                            pass
                        else:
                            empty_parent_slice = False
                            yield {stream_state_field: stream_state_value, "parent_slice": parent_slice}
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield from []
