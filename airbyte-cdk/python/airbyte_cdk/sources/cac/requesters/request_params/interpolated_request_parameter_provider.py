#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.requesters.request_params.request_parameters_provider import RequestParameterProvider


class InterpolatedRequestParameterProvider(RequestParameterProvider):
    def __init__(self, request_parameters: Mapping[str, str], config):
        self._interpolation = JinjaInterpolation()
        self._request_parameters = request_parameters
        self._config = config
        self._vars = dict()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}

        return {
            self._interpolation.eval(name, self._vars, self._config, **kwargs): self._interpolation.eval(
                value, self._vars, self._config, **kwargs
            )
            for name, value in self._request_parameters.items()
        }
