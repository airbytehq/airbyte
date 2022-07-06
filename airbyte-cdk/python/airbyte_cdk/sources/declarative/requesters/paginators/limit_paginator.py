#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Any, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.types import Config


class RequestOptionType(Enum):
    request_parameter = "request_parameter"
    header = "header"
    path = "path"
    body_data = "body_data"
    body_json = "body_json"


class RequestOption:
    def __init__(self, option_type: Union[RequestOptionType, str] = None, field_name=None):
        if isinstance(option_type, str):
            option_type = RequestOptionType[option_type]
        self._option_type = option_type
        self._field_name = field_name


class PaginationStrategy:
    pass


class LimitPaginator:
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

        if limit_option._option_type == RequestOptionType.path:
            raise ValueError("Limit parameter cannot be a path")
        self._config = config
        self._limit = limit_value
        self._limit_option = limit_option
        self._page_token = page_token
        # FIXME also need to pass in those from the strategy...
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
        if self._token and self._page_token._option_type == RequestOptionType.path:
            return self._token.replace(self._url_base, "")
        else:
            return None

    def request_params(self) -> MutableMapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def request_headers(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.header)

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return self._get_request_options(RequestOptionType.body_data)

    def request_body_json(self) -> Optional[Mapping]:
        return self._get_request_options(RequestOptionType.body_json)

    def _get_request_options(self, option_type):
        options = {}
        if self._page_token._option_type == option_type:
            if option_type != RequestOptionType.path:
                options[self._page_token._field_name] = self._token
        if self._limit_option._option_type == option_type:
            options[self._limit_option._field_name] = self._limit
        return options
