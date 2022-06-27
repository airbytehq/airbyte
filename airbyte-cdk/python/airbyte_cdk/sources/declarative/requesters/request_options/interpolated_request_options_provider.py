#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider


class InterpolatedRequestOptionsProvider(RequestOptionsProvider):
    def __init__(self, *, config, request_parameters=None, request_headers=None, request_body_data=None, request_body_json=None):
        if request_parameters is None:
            request_parameters = {}
        if request_headers is None:
            request_headers = {}
        if request_body_data is None:
            request_body_data = ""
        if request_body_json is None:
            request_body_json = {}

        if request_body_json and request_body_data:
            raise ValueError("RequestOptionsProvider should only contain either 'request_body_data' or 'request_body_json' not both")

        self._parameter_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_parameters)
        self._headers_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_headers)
        self._body_data_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_body_data)
        self._body_json_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_body_json)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        interpolated_value = self._parameter_interpolator.request_inputs(stream_state, stream_slice, next_page_token)
        if isinstance(interpolated_value, dict):
            return interpolated_value
        return {}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return self._headers_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Union[Mapping, str]]:
        return self._body_data_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        return self._body_json_interpolator.request_inputs(stream_state, stream_slice, next_page_token)

    def request_kwargs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # todo: there are a few integrations that override the request_kwargs() method, but the use case for why kwargs over existing
        #  constructs is a little unclear. We may revisit this, but for now lets leave it out of the DSL
        return {}
