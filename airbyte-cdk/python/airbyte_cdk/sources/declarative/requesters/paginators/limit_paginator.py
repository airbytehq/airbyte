#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.types import Config


class RequestOption:
    def __init__(self, value, option_type, field_name=None):
        self._value = value
        self._option_type = option_type
        self._field_name = field_name


class LimitPaginator:
    """
    A paginator that performs pagination by incrementing a page number and stops based on a provided stop condition.
    """

    def __init__(
        self,
        limit: RequestOption,
        next_page_token: RequestOption,
        config: Config,
        url_base: str = None,
    ):
        self._limit = limit
        self._next_page_token = next_page_token
        self._config = config
        self._request_options_provider, self._path = self._createRequestOptionsProvider([self._limit, self._next_page_token])
        self._token = None
        self._url_base = url_base

    def _createRequestOptionsProvider(self, request_options: List[RequestOption]):
        request_params = {}
        # headers = {}
        path = None
        for option in request_options:
            if option._option_type == "request_parameter":
                request_params[option._field_name] = option._value
            if option._option_type == "path":
                if path:
                    raise Exception()
                else:
                    path = option._value
        return InterpolatedRequestOptionsProvider(request_parameters=request_params, config=self._config), path

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        print(f"len of last_records: {len(last_records)}")
        if len(last_records) < self._limit._value:
            return None
        else:
            next_page = {
                "next_page_token": InterpolatedString(self._next_page_token._value).eval(
                    config=self._config, decoded_response=response.json()
                )
            }
            self._token = next_page
        return next_page

    def path(self):
        if self._token:
            return self._token["next_page_token"].replace(self._url_base, "")
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return self._request_options_provider.request_params(stream_state, stream_slice, next_page_token)

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return self._request_options_provider.request_headers(stream_state, stream_slice, next_page_token)

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Union[Mapping, str]]:
        return self._request_options_provider.request_body_data(stream_state, stream_slice, next_page_token)

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        return self._request_options_provider.request_body_json(stream_state, stream_slice, next_page_token)
