#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator import ConditionalPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.types import Config


class LimitPaginator(ConditionalPaginator, JsonSchemaMixin):
    def __init__(
        self,
        limit_value: int,
        limit_option: RequestOption,
        page_token: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config = {},
        decoder: Decoder = None,
        url_base: str = None,
    ):
        self._config = config
        self._limit = limit_value

        super().__init__(
            self.stop_condition,
            self._create_request_options_provider(limit_value, limit_option),
            page_token,
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
