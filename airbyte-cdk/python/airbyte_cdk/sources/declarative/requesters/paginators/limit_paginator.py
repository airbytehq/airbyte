#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.paginators.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.types import Config


class LimitPaginator(Paginator):
    """
    A paginator that performs pagination by incrementing a page number and stops based on a provided stop condition.
    """

    def __init__(
        self,
        limit_value: int,
        limit_option: RequestOption,
        page_token: RequestOption,
        pagination_strategy: PaginationStrategy,
        config: Config,
        url_base: str = None,
    ):
        if limit_option.option_type == RequestOptionType.path:
            raise ValueError("Limit parameter cannot be a path")
        self._config = config
        self._limit = limit_value
        self._limit_option = limit_option
        self._page_token = page_token
        self._pagination_strategy = pagination_strategy
        self._token = None
        self._url_base = url_base

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        if len(last_records) < self._limit:
            return None
        else:
            self._token = self._pagination_strategy.next_page_token(response, last_records)
            return {"next_page_token": self._token}

    def path(self):
        if self._token and self._page_token.option_type == RequestOptionType.path:
            return self._token.replace(self._url_base, "")
        else:
            return None

    def request_params(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def request_headers(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.header)

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return self._get_request_options(RequestOptionType.body_data)

    def request_body_json(self) -> Optional[Mapping]:
        return self._get_request_options(RequestOptionType.body_json)

    def _get_request_options(self, option_type):
        options = {}
        if self._page_token.option_type == option_type:
            if option_type != RequestOptionType.path:
                options[self._page_token._field_name] = self._token
        if self._limit_option.option_type == option_type:
            options[self._limit_option.field_name] = self._limit
        return options
