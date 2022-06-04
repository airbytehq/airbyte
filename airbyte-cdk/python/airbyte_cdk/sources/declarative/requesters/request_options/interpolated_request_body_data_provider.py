#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider import InterpolatedRequestInputProvider


class InterpolatedRequestBodyDataProvider:
    """
    Helper class that allows for performing interpolation on either a string or a map depending on the request_inputs type
    """

    def __init__(self, *, config, request_inputs=None):
        if request_inputs is None:
            request_inputs = ""
        self._config = config

        if isinstance(request_inputs, dict):
            self._body_data_map_interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_inputs)
            self._body_data_string_interpolator = None
        else:
            self._body_data_string_interpolator = InterpolatedString(string=request_inputs, default="")
            self._body_data_map_interpolator = None

    def request_inputs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Union[Mapping, str]]:
        if self._body_data_string_interpolator is None:
            return self._body_data_map_interpolator.request_inputs(stream_state, stream_slice, next_page_token)
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return self._body_data_string_interpolator.eval(self._config, **kwargs)
