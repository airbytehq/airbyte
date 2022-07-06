#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.types import Config


class InterpolatedPaginator(Paginator):
    def path(self) -> Optional[str]:
        pass

    def request_params(self) -> Mapping[str, Any]:
        pass

    def request_headers(self) -> Mapping[str, Any]:
        pass

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        pass

    def request_body_json(self) -> Optional[Mapping]:
        pass

    def __init__(self, *, next_page_token_template: Mapping[str, str], config: Config, decoder: Optional[Decoder] = None):
        self._next_page_token_template = InterpolatedMapping(next_page_token_template, JinjaInterpolation())
        self._decoder = decoder or JsonDecoder()
        self._config = config

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        decoded_response = self._decoder.decode(response)
        headers = response.headers
        interpolated_values = self._next_page_token_template.eval(
            self._config, decoded_response=decoded_response, headers=headers, last_records=last_records
        )

        non_null_tokens = {k: v for k, v in interpolated_values.items() if v is not None}

        return non_null_tokens if non_null_tokens else None
