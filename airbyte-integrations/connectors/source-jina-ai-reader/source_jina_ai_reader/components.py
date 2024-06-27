#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_input_provider import InterpolatedRequestInputProvider
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class JinaAiHttpRequester(HttpRequester):
    request_headers: Optional[Union[str, Mapping[str, str]]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._headers_interpolator = InterpolatedRequestInputProvider(
            config=self.config, request_inputs=self.request_headers, parameters=parameters
        )

    # For appending bearer token only if api_key is present
    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        headers = self._headers_interpolator.eval_request_inputs(stream_state, stream_slice, next_page_token)
        if isinstance(headers, dict):
            api_key = self.config.get("api_key")
            if api_key:
                headers.update({"Authorization": f"Bearer {api_key}"})
            return headers
        return {}
