#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState

RequestInput = Union[str, Mapping[str, str]]


class InterpolatedRequestOptionsProvider(RequestOptionsProvider):
    """Defines the request options to set on an outgoing HTTP request by evaluating `InterpolatedMapping`s"""

    def __init__(
        self,
        *,
        config: Config,
        request_parameters: Optional[RequestInput] = None,
        request_headers: Optional[RequestInput] = None,
        request_body_data: Optional[RequestInput] = None,
        request_body_json: Optional[RequestInput] = None,
    ):
        """
        :param config: The user-provided configuration as specified by the source's spec
        :param request_parameters: The request parameters to set on an outgoing HTTP request
        :param request_headers: The request headers to set on an outgoing HTTP request
        :param request_body_data: The body data to set on an outgoing HTTP request
        :param request_body_json: The json content to set on an outgoing HTTP request
        """
        if request_parameters is None:
            request_parameters = {}
        if request_headers is None:
            request_headers = {}
        if request_body_data is None:
            request_body_data = {}
        if request_body_json is None:
            request_body_json = {}

        if request_body_json and request_body_data:
            raise ValueError("RequestOptionsProvider should only contain either 'request_body_data' or 'request_body_json' not both")

        self._parameter_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_parameters)
        self._headers_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_headers)
        self._body_data_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_body_data)
        self._body_json_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_body_json)

    def request_params(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> MutableMapping[str, Any]:
        interpolated_value = self._parameter_interpolator.request_inputs(stream_state, stream_slice, next_page_token)
        if isinstance(interpolated_value, dict):
            return interpolated_value
        return {}

    def request_headers(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Mapping[str, Any]:
        return self._headers_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def request_body_data(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Optional[Union[Mapping, str]]:
        return self._body_data_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def request_body_json(
        self,
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        return self._body_json_interpolator.request_inputs(stream_state, stream_slice, next_page_token)
