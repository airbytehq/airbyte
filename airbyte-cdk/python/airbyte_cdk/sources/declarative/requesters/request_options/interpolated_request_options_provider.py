#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

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

    def request_params(self, **kwargs) -> Mapping[str, Any]:
        interpolated_value = self._parameter_interpolator.request_inputs(**kwargs)
        if isinstance(interpolated_value, dict):
            return interpolated_value
        return {}

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return self._headers_interpolator.request_inputs(**kwargs)

    def request_body_data(self, **kwargs) -> Mapping[str, Any]:
        return self._body_data_interpolator.request_inputs(**kwargs)

    def request_body_json(self, **kwargs) -> Mapping[str, Any]:
        return self._body_json_interpolator.request_inputs(**kwargs)
