#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Callable, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.paginators.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.types import Config


class ConditionalPaginator(Paginator):
    """
    A paginator that performs pagination by incrementing a page number and stops based on a provided stop condition.
    """

    def __init__(
        self,
        stop_condition: Callable[[requests.Response, List[Mapping[str, Any]]], bool],
        request_options_provider: InterpolatedRequestOptionsProvider,
        page_token: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str = None,
    ):
        self._stop_condition = stop_condition
        self._request_options_provider = request_options_provider
        self._config = config
        self._page_token = page_token
        self._pagination_strategy = pagination_strategy
        self._token = None
        self._url_base = url_base

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        if self._stop_condition(response, last_records):
            return None
        else:
            self._token = self._pagination_strategy.next_page_token(response, last_records)
            if self._token:
                return {"next_page_token": self._token}
            else:
                return None

    def path(self):
        if self._token and self._page_token.option_type == RequestOptionType.path:
            return self._token.replace(self._url_base, "")
        else:
            return None

    def request_params(self) -> Mapping[str, Any]:
        return {
            **self._get_request_options(RequestOptionType.request_parameter),
            **self._request_options_provider.request_params(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def request_headers(self) -> Mapping[str, Any]:
        return {
            **self._get_request_options(RequestOptionType.header),
            **self._request_options_provider.request_headers(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return {
            **self._get_request_options(RequestOptionType.body_data),
            **self._request_options_provider.request_headers(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def request_body_json(self) -> Optional[Mapping]:
        return {
            **self._get_request_options(RequestOptionType.body_json),
            **self._request_options_provider.request_body_json(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def _get_request_options(self, option_type):
        options = {}
        if self._page_token.option_type == option_type:
            if option_type != RequestOptionType.path and self._token:
                options[self._page_token.field_name] = self._token
        return options


class InterpolatedConditionalPaginator(ConditionalPaginator):
    def __init__(
        self,
        stop_condition: str,
        decoder: Decoder,
        request_options_provider: InterpolatedRequestOptionsProvider,
        page_token: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str = None,
    ):
        self._stop_condition_interpolator = InterpolatedBoolean(stop_condition)
        self._decoder = decoder
        super().__init__(self.stop_condition, request_options_provider, page_token, pagination_strategy, config, url_base)

    def stop_condition(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> bool:
        decoded_response = self._decoder.decode(response)
        headers = response.headers
        should_stop = self._stop_condition_interpolator.eval(
            self._config, decoded_response=decoded_response, headers=headers, last_records=last_records
        )
        return should_stop
