#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


@dataclass
class ListPartitionRouter(StreamSlicer):
    """
    Partition router that iterates over the values of a list
    If values is a string, then evaluate it as literal and assert the resulting literal is a list

    Attributes:
        values (Union[str, List[str]]): The values to iterate over
        cursor_field (Union[InterpolatedString, str]): The name of the cursor field
        config (Config): The user-provided configuration as specified by the source's spec
        request_option (Optional[RequestOption]): The request option to configure the HTTP request
    """

    values: Union[str, List[str]]
    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    request_option: Optional[RequestOption] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        if isinstance(self.values, str):
            self.values = InterpolatedString.create(self.values, parameters=parameters).eval(self.config)
        if isinstance(self.cursor_field, str):
            self.cursor_field = InterpolatedString(string=self.cursor_field, parameters=parameters)

        self._cursor = None

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
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def stream_slices(self) -> Iterable[StreamSlice]:
        return [{self.cursor_field.eval(self.config): slice_value} for slice_value in self.values]

    def _get_request_option(self, request_option_type: RequestOptionType, stream_slice: StreamSlice):
        if self.request_option and self.request_option.inject_into == request_option_type and stream_slice:
            slice_value = stream_slice.get(self.cursor_field.eval(self.config))
            if slice_value:
                return {self.request_option.field_name: slice_value}
            else:
                return {}
        else:
            return {}
