#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class ListStreamSlicer(StreamSlicer, JsonSchemaMixin):
    """
    Stream slicer that iterates over the values of a list
    If slice_values is a string, then evaluate it as literal and assert the resulting literal is a list

    Attributes:
        slice_values (Union[str, List[str]]): The values to iterate over
        cursor_field (Union[InterpolatedString, str]): The name of the cursor field
        config (Config): The user-provided configuration as specified by the source's spec
        request_option (Optional[RequestOption]): The request option to configure the HTTP request
    """

    slice_values: Union[str, List[str]]
    cursor_field: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    request_option: Optional[RequestOption] = None

    def __post_init__(self, options: Mapping[str, Any]):
        if isinstance(self.slice_values, str):
            self.slice_values = InterpolatedString.create(self.slice_values, options=options).eval(self.config)
        if isinstance(self.cursor_field, str):
            self.cursor_field = InterpolatedString(string=self.cursor_field, options=options)

        if self.request_option and self.request_option.inject_into == RequestOptionType.path:
            raise ValueError("Slice value cannot be injected in the path")
        self._cursor = None

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        slice_value = stream_slice.get(self.cursor_field.eval(self.config))
        if slice_value and slice_value in self.slice_values:
            self._cursor = slice_value

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field.eval(self.config): self._cursor} if self._cursor else {}

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_option(RequestOptionType.request_parameter)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_option(RequestOptionType.header)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_option(RequestOptionType.body_data)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_option(RequestOptionType.body_json)

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        return [{self.cursor_field.eval(self.config): slice_value} for slice_value in self.slice_values]

    def _get_request_option(self, request_option_type: RequestOptionType):
        if self.request_option and self.request_option.inject_into == request_option_type:
            return {self.request_option.field_name: self._cursor}
        else:
            return {}
