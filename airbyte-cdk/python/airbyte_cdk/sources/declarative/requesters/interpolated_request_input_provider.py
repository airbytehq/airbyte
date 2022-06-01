#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


class InterpolatedRequestInputProvider:
    """
    Helper class that generically performs string interpolation on the provided dictionary input
    """

    def __init__(self, *, config, request_inputs=None):
        if request_inputs is None:
            request_inputs = {}
        self._interpolator = InterpolatedMapping(request_inputs, JinjaInterpolation())
        self._config = config

    def request_inputs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        interpolated_values = self._interpolator.eval(self._config, **kwargs)  # dig into this function a little more
        non_null_tokens = {k: v for k, v in interpolated_values.items() if v}
        return non_null_tokens
