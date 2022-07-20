#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.types import Config


class LimitPaginator(Paginator):
    """
    Limit paginator.
    Requests pages of results with a maximum number of records defined by limit_value.

    Examples:
        1.
        * fetches up to 10 records at a time by setting the "limit" request param to 10
        * updates the request path with  "{{ decoded_response._metadata.next }}"
          paginator:
            type: "LimitPaginator"
            limit_value: 10
            limit_option:
              option_type: request_parameter
              field_name: page_size
            page_token_option:
              option_type: path
            pagination_strategy:
              type: "CursorPagination"
              cursor_value: "{{ decoded_response._metadata.next }}"
        `

        2.
        * fetches up to 5 records at a time by setting the "page_size" header to 5
        * increments a record counter and set the request parameter "offset" to the value of the counter
        `
          paginator:
            type: "LimitPaginator"
            limit_value: 5
            limit_option:
              option_type: header
              field_name: page_size
            pagination_strategy:
              type: "OffsetIncrement"
            page_token:
              option_type: "request_parameter"
              field_name: "offset"
        `

        3.
        * fetches up to 5 records at a time by setting the "page_size" request param to 5
        * increments a page counter and set the request parameter "page" to the value of the counter
        `
          paginator:
            type: "LimitPaginator"
            limit_value: 5
            limit_option:
              option_type: request_parameter
              field_name: page_size
            pagination_strategy:
              type: "PageIncrement"
            page_token:
              option_type: "request_parameter"
              field_name: "page"
        `

    """

    def __init__(
        self,
        page_size: int,
        limit_option: RequestOption,
        page_token_option: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str,
        decoder: Decoder = None,
    ):
        """
        :param page_size: the number of records to request
        :param limit_option: the request option to set the limit
        :param page_token_option: the request option to set the page token
        :param pagination_strategy: Strategy defining how to get the next page token
        :param config: connection config
        :param url_base: endpoint's base url
        :param decoder: decoder to decode the response
        """
        self._page_size = page_size
        self._config = config
        self._request_options_provider = self._create_request_options_provider(page_size, limit_option)
        self._page_token_option = page_token_option
        self._pagination_strategy = pagination_strategy
        self._token = None
        if isinstance(url_base, str):
            url_base = InterpolatedString(url_base)
        self._url_base = url_base
        self._decoder = decoder or JsonDecoder()

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        self._token = self._pagination_strategy.next_page_token(response, last_records)
        if self._token:
            return {"next_page_token": self._token}
        else:
            return None

    def path(self):
        if self._token and self._page_token_option.option_type == RequestOptionType.path:
            # Replace url base to only return the path
            return str(self._token).replace(self._url_base.eval(self._config), "")
        else:
            return None

    def request_params(self) -> Mapping[str, Any]:
        return {
            **self._get_request_options(RequestOptionType.request_parameter),
            **self._request_options_provider.request_params(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def request_headers(self) -> Mapping[str, str]:
        return {
            **self._get_request_options(RequestOptionType.header),
            **self._request_options_provider.request_headers(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def request_body_data(self) -> Union[Mapping[str, Any], str]:
        # the request body data coming from the provider can be a string of the form
        # "k1=v1&k2=v2"
        request_options = self._get_request_options(RequestOptionType.body_data)
        request_options_from_provider = (
            self._request_options_provider.request_body_data(stream_state=None, stream_slice=None, next_page_token=None) or {}
        )
        if request_options_from_provider and isinstance(request_options_from_provider, str):
            # convert request_options to "k1=v1&k2=v2" string then join the request options
            return "&".join([*[f"{k}={v}" for k, v in request_options.items()], request_options_from_provider])
        else:
            return {**request_options, **request_options_from_provider}

    def request_body_json(self) -> Mapping[str, Any]:
        return {
            **self._get_request_options(RequestOptionType.body_json),
            **self._request_options_provider.request_body_json(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def _get_request_options(self, option_type) -> Mapping[str, Any]:
        options = {}
        if self._page_token_option.option_type == option_type:
            if option_type != RequestOptionType.path and self._token:
                options[self._page_token_option.field_name] = self._token
        return options

    def _create_request_options_provider(self, limit_value, limit_option: RequestOption):
        if limit_option.option_type == RequestOptionType.path:
            raise ValueError("Limit parameter cannot be a path")
        elif limit_option.option_type == RequestOptionType.request_parameter:
            return InterpolatedRequestOptionsProvider(request_parameters={limit_option.field_name: limit_value}, config=self._config)
        elif limit_option.option_type == RequestOptionType.header:
            return InterpolatedRequestOptionsProvider(request_headers={limit_option.field_name: limit_value}, config=self._config)
        elif limit_option.option_type == RequestOptionType.body_json:
            return InterpolatedRequestOptionsProvider(request_body_json={limit_option.field_name: limit_value}, config=self._config)
        elif limit_option.option_type == RequestOptionType.body_data:
            return InterpolatedRequestOptionsProvider(request_body_data={limit_option.field_name: limit_value}, config=self._config)
        else:
            raise ValueError(f"Unexpected request option type. Got :{limit_option}")
