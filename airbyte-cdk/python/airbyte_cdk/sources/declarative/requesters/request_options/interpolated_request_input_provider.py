#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


@dataclass
class InterpolatedRequestInputProvider:
    """
    Helper class that generically performs string interpolation on the provided dictionary or string input
    """

    options: InitVar[Mapping[str, Any]]
    request_inputs: Optional[Union[str, Mapping[str, str]]] = field(default=None)
    config: Config = field(default_factory=dict)
    _interpolator: Union[InterpolatedString, InterpolatedMapping] = field(init=False, repr=False, default=None)
    _request_inputs: Union[str, Mapping[str, str]] = field(init=False, repr=False, default=None)

    def __post_init__(self, options: Mapping[str, Any]):

        self._request_inputs = self.request_inputs or {}
        if isinstance(self.request_inputs, str):
            self._interpolator = InterpolatedString(self.request_inputs, default="", options=options)
        else:
            self._interpolator = InterpolatedMapping(self._request_inputs, options=options)

    def eval_request_inputs(
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
        interpolated_value = self._interpolator.eval(self.config, **kwargs)

        if isinstance(interpolated_value, dict):
            non_null_tokens = {k: v for k, v in interpolated_value.items() if v is not None}
            return non_null_tokens
        return interpolated_value
