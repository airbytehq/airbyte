#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_nested_mapping import InterpolatedNestedMapping, NestedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class InterpolatedNestedRequestInputProvider:
    """
    Helper class that generically performs string interpolation on a provided deeply nested dictionary or string input
    """

    parameters: InitVar[Mapping[str, Any]]
    request_inputs: Optional[Union[str, NestedMapping]] = field(default=None)
    config: Config = field(default_factory=dict)
    _interpolator: Optional[Union[InterpolatedString, InterpolatedNestedMapping]] = field(init=False, repr=False, default=None)
    _request_inputs: Optional[Union[str, NestedMapping]] = field(init=False, repr=False, default=None)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:

        self._request_inputs = self.request_inputs or {}
        if isinstance(self._request_inputs, str):
            self._interpolator = InterpolatedString(self._request_inputs, default="", parameters=parameters)
        else:
            self._interpolator = InterpolatedNestedMapping(self._request_inputs, parameters=parameters)

    def eval_request_inputs(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Returns the request inputs to set on an outgoing HTTP request

        :param stream_state: The stream state
        :param stream_slice: The stream slice
        :param next_page_token: The pagination token
        :return: The request inputs to set on an outgoing HTTP request
        """
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return self._interpolator.eval(self.config, **kwargs)  # type: ignore  # self._interpolator is always initialized with a value and will not be None
