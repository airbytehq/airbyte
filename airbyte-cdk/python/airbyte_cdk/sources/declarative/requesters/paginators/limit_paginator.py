#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.types import Config


class LimitPaginator(Paginator):
    """
    Limit paginator to request pages of results with a fixed size until the pagination strategy no longer returns a next_page_token

    Examples:
        1.
        * fetches up to 10 records at a time by setting the "limit" request param to 10
        * updates the request path with  "{{ response._metadata.next }}"
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
              cursor_value: "{{ response._metadata.next }}"
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
        **options: Optional[Mapping[str, Any]],
    ):
        """
        :param page_size: The number of records to request
        :param limit_option: The request option to set the limit. Cannot be injected in the path.
        :param page_token_option: The request option to set the page token
        :param pagination_strategy: The strategy defining how to get the next page token
        :param config: The user-provided configuration as specified by the source's spec
        :param url_base: The endpoint's base url
        :param decoder: The decoder to decode the response
        :param options: Additional runtime parameters to be used for string interpolation
        """
        if limit_option.inject_into == RequestOptionType.path:
            raise ValueError("Limit parameter cannot be a path")
        self._page_size = page_size
        self._config = config
        self._limit_option = limit_option
        self._page_token_option = page_token_option
        self._pagination_strategy = pagination_strategy
        self._token = None
        if isinstance(url_base, str):
            url_base = InterpolatedString.create(url_base, options=options)
        self._url_base = url_base
        self._decoder = decoder or JsonDecoder()

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        self._token = self._pagination_strategy.next_page_token(response, last_records)
        if self._token:
            return {"next_page_token": self._token}
        else:
            return None

    def path(self):
        if self._token and self._page_token_option.inject_into == RequestOptionType.path:
            # Replace url base to only return the path
            return str(self._token).replace(self._url_base.eval(self._config), "")
        else:
            return None

    def request_params(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def request_headers(self) -> Mapping[str, str]:
        return self._get_request_options(RequestOptionType.header)

    def request_body_data(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_data)

    def request_body_json(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_json)

    def request_kwargs(self) -> Mapping[str, Any]:
        # Never update kwargs
        return {}

    def _get_request_options(self, option_type: RequestOptionType) -> Mapping[str, Any]:
        options = {}
        if self._page_token_option.inject_into == option_type:
            if option_type != RequestOptionType.path and self._token:
                options[self._page_token_option.field_name] = self._token
        if self._limit_option.inject_into == option_type:
            if option_type != RequestOptionType.path:
                options[self._limit_option.field_name] = self._page_size
        return options
