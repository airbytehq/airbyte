#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator import ConditionalPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.types import Config


class LimitPaginator(ConditionalPaginator):
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
        limit_value: int,
        limit_option: RequestOption,
        page_token_option: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str,
        decoder: Decoder = None,
    ):
        """

        :param limit_value: the number of records to request
        :param limit_option: the request option to set the limit
        :param page_token_option: the request option to set the page token
        :param pagination_strategy: Strategy defining how to get the next page token
        :param config: connection config
        :param url_base: endpoint's base url
        :param decoder: decoder to decode the response
        """
        self._config = config
        self._limit = limit_value

        super().__init__(
            self._create_request_options_provider(limit_value, limit_option),
            page_token_option,
            pagination_strategy,
            config,
            url_base,
            decoder,
        )

    def stop_condition(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> bool:
        return len(last_records) < self._limit

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
