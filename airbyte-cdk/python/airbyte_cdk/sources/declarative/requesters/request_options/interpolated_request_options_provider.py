#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin

RequestInput = Union[str, Mapping[str, str]]


@dataclass
class InterpolatedRequestOptionsProvider(RequestOptionsProvider, JsonSchemaMixin):
    """
    Defines the request options to set on an outgoing HTTP request by evaluating `InterpolatedMapping`s

    Attributes:
        config (Config): The user-provided configuration as specified by the source's spec
        request_parameters (Union[str, Mapping[str, str]]): The request parameters to set on an outgoing HTTP request
        request_headers (Union[str, Mapping[str, str]]): The request headers to set on an outgoing HTTP request
        request_body_data (Union[str, Mapping[str, str]]): The body data to set on an outgoing HTTP request
        request_body_json (Union[str, Mapping[str, str]]): The json content to set on an outgoing HTTP request
    """

    options: InitVar[Mapping[str, Any]]
    config: Config = field(default_factory=dict)
    request_parameters: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None
    request_body_json: Optional[RequestInput] = None

    def __post_init__(self, options: Mapping[str, Any]):
        if self.request_parameters is None:
            self.request_parameters = {}
        if self.request_headers is None:
            self.request_headers = {}
        if self.request_body_data is None:
            self.request_body_data = {}
        if self.request_body_json is None:
            self.request_body_json = {}

        if self.request_body_json and self.request_body_data:
            raise ValueError("RequestOptionsProvider should only contain either 'request_body_data' or 'request_body_json' not both")

        self._parameter_interpolator = InterpolatedRequestInputProvider(config=self.config, request_inputs=self.request_parameters)
        self._headers_interpolator = InterpolatedRequestInputProvider(config=self.config, request_inputs=self.request_headers)
        self._body_data_interpolator = InterpolatedRequestInputProvider(config=self.config, request_inputs=self.request_body_data)
        self._body_json_interpolator = InterpolatedRequestInputProvider(config=self.config, request_inputs=self.request_body_json)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        interpolated_value = self._parameter_interpolator.request_inputs(stream_state, stream_slice, next_page_token)
        if isinstance(interpolated_value, dict):
            return interpolated_value
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._headers_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Union[Mapping, str]]:
        return self._body_data_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        return self._body_json_interpolator.request_inputs(stream_state, stream_slice, next_page_token)
