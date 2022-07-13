#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.types import Config


class ConditionalPaginator(Paginator, ABC):
    """
    A paginator that performs pagination by incrementing a page number and stops based on a provided stop condition.

    next_page_token() updates self._token with the token, and returns {"next_page_token: token}
    path, request_params, request_headers, request_body_data, and request_body_json return the request options to set using self._token set by next_page_token
    """

    def __init__(
        self,
        request_options_provider: InterpolatedRequestOptionsProvider,
        page_token_option: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str,
        decoder: Decoder = None,
    ):
        """
        :param request_options_provider: additional request options to set
        :param page_token_option: request option to set the the next_page_token
        :param pagination_strategy: Strategy defining how to get the next page token
        :param config: connection config
        :param url_base: endpoint's base url
        :param decoder: decoder to decode the response
        """
        self._request_options_provider = request_options_provider
        self._config = config
        self._page_token_option = page_token_option
        self._pagination_strategy = pagination_strategy
        self._token = None
        self._url_base = url_base
        self._decoder = decoder or JsonDecoder()

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        """
        Returns a mapping {"next_page_token": <token>}
        This is required to tell HttpStream there is another page to request.

        :param response: to process
        :param last_records: records extracted from the response
        :return: mapping {"next_page_token": token}
        """
        if self.stop_condition(response, last_records):
            return None
        else:
            self._token = self._pagination_strategy.next_page_token(response, last_records)
            if self._token:
                return {"next_page_token": self._token}
            else:
                return None

    @abstractmethod
    def stop_condition(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> bool:
        """
        Predicate evaluating to True when there are no more pages to request
        :param response:
        :param last_records:
        :return: boolean indicating whether we should stop paginating
        """

    def path(self):
        if self._token and self._page_token_option.option_type == RequestOptionType.path:
            # Replace url base to only return the path
            return self._token.replace(self._url_base, "")
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
        return {
            **self._get_request_options(RequestOptionType.body_data),
            **self._request_options_provider.request_headers(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def request_body_json(self) -> Mapping[str, Any]:
        return {
            **self._get_request_options(RequestOptionType.body_json),
            **self._request_options_provider.request_body_json(stream_state=None, stream_slice=None, next_page_token=None),
        }

    def _get_request_options(self, option_type):
        options = {}
        if self._page_token_option.option_type == option_type:
            if option_type != RequestOptionType.path and self._token:
                options[self._page_token_option.field_name] = self._token
        return options


class InterpolatedConditionalPaginator(ConditionalPaginator, JsonSchemaMixin):
    """

    example:
    * stops paginating when "{{ decoded_response._metadata.self == decoded_response._metadata.next }}"
    * sets "page_size" request param to 10
    * updates the path with "{{ decoded_response._metadata.next }}"
    `
      paginator:
        class_name: "airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator.InterpolatedConditionalPaginator"
        stop_condition: "{{ decoded_response._metadata.self == decoded_response._metadata.next }}"
        request_options_provider:
          request_parameters:
            page_size: 10
        page_token_option:
          option_type: path
        pagination_strategy:
          type: "CursorPagination"
          cursor_value: "{{ decoded_response._metadata.next }}"
    `
    """

    def __init__(
        self,
        stop_condition: InterpolatedBoolean,
        request_options_provider: InterpolatedRequestOptionsProvider,
        page_token_option: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str = None,
        decoder: Decoder = None,
    ):
        """

        :param stop_condition: Interpolated string to evaluate defining when to stop paginating
        :param request_options_provider: additional request options to set
        :param page_token_option: request option to set the the next_page_token
        :param pagination_strategy: Strategy defining how to get the next page token
        :param config: connection config
        :param url_base: endpoint's base url
        :param decoder: decoder to decode the response
        """
        self._decoder = decoder
        self._stop_condition_interpolator = stop_condition
        super().__init__(request_options_provider, page_token_option, pagination_strategy, config, url_base, decoder)

    def stop_condition(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> bool:
        decoded_response = self._decoder.decode(response)
        headers = response.headers
        should_stop = self._stop_condition_interpolator.eval(
            self._config, decoded_response=decoded_response, headers=headers, last_records=last_records
        )
        return should_stop
