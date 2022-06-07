#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.requesters.request_headers.request_header_provider import RequestHeaderProvider


class InterpolatedRequestHeaderProvider(RequestHeaderProvider):
    """
    Provider that takes in a dictionary of request headers and performs string interpolation on the defined templates and static
    values based on the current state of stream being processed
    """

    def __init__(self, *, config, request_headers):
        self._interpolator = InterpolatedRequestInputProvider(config=config, request_inputs=request_headers)

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return self._interpolator.request_inputs(stream_state, stream_slice, next_page_token)
