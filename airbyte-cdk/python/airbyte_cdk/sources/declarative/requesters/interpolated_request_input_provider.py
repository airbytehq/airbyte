#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


class InterpolatedRequestInputProvider:
    """
    Helper class that generically performs string interpolation on the provided dictionary or string input
    """

    def __init__(
        self, *, config: Config, request_inputs: Optional[Union[str, Mapping[str, str]]] = None, **options: Optional[Mapping[str, Any]]
    ):
        """
        :param config: The user-provided configuration as specified by the source's spec
        :param request_inputs: The dictionary to interpolate
        :param options: Additional runtime parameters to be used for string interpolation
        """

        self._config = config

        if request_inputs is None:
            request_inputs = {}
        if isinstance(request_inputs, str):
            self._interpolator = InterpolatedString(request_inputs, default="", options=options)
        else:
            self._interpolator = InterpolatedMapping(request_inputs, options=options)

    def request_inputs(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Returns the request inputs to set on an outgoing HTTP request

        :param stream_state: The stream state
        :param stream_slice: The stream slice
        :param next_page_token: The pagination token
        :return: The request inputs to set on an outgoing HTTP request
        """
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        interpolated_value = self._interpolator.eval(self._config, **kwargs)

        if isinstance(interpolated_value, dict):
            non_null_tokens = {k: v for k, v in interpolated_value.items() if v}
            return non_null_tokens
        return interpolated_value
