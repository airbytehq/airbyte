#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.cac.requesters.request_params.request_parameters_provider import RequestParameterProvider


class InterpolatedRequestParameterProvider(RequestParameterProvider):
    def __init__(self, *, config, request_parameters=None):
        if request_parameters is None:
            request_parameters = dict()
        request_parameters = request_parameters
        self._interpolation = InterpolatedMapping(request_parameters, JinjaInterpolation())
        self._config = config

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return self._interpolation.eval(self._config, **kwargs)
