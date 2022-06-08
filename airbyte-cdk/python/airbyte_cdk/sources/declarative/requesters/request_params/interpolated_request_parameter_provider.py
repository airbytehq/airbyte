#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.requesters.request_params.request_parameters_provider import RequestParameterProvider


class InterpolatedRequestParameterProvider(RequestParameterProvider):
    def __init__(self, *, config, request_parameters=None):
        if request_parameters is None:
            request_parameters = {}
        self._interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_parameters)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return self._interpolator.request_inputs(stream_state, stream_slice, next_page_token)
