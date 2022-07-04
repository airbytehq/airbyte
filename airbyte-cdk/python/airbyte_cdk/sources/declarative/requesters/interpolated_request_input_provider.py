#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedRequestInputProvider:
    """
    Helper class that generically performs string interpolation on the provided dictionary or string input
    """

    def __init__(self, *, config, request_inputs=None):
        self._config = config

        if request_inputs is None:
            request_inputs = {}
        if isinstance(request_inputs, str):
            self._interpolator = InterpolatedString(request_inputs, "")
        else:
            self._interpolator = InterpolatedMapping(request_inputs, JinjaInterpolation())

    def request_inputs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Union[Mapping, str]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        interpolated_value = self._interpolator.eval(self._config, **kwargs)

        if isinstance(interpolated_value, dict):
            non_null_tokens = {k: v for k, v in interpolated_value.items() if v}
            return non_null_tokens
        return interpolated_value
