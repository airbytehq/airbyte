#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DefaultPaginator(Paginator, JsonSchemaMixin):
    """
    Default paginator to request pages of results with a fixed size until the pagination strategy no longer returns a next_page_token

    Examples:
        1.
        * fetches up to 10 records at a time by setting the "limit" request param to 10
        * updates the request path with  "{{ response._metadata.next }}"
        ```
          paginator:
            type: "DefaultPaginator"
            page_size_option:
              inject_into: request_parameter
              field_name: limit
            page_token_option:
              option_type: path
            pagination_strategy:
              type: "CursorPagination"
              cursor_value: "{{ response._metadata.next }}"
              page_size: 10
        ```

        2.
        * fetches up to 5 records at a time by setting the "page_size" header to 5
        * increments a record counter and set the request parameter "offset" to the value of the counter
        ```
          paginator:
            type: "DefaultPaginator"
            page_size_option:
              inject_into: header
              field_name: page_size
            pagination_strategy:
              type: "OffsetIncrement"
              page_size: 5
            page_token_option:
              option_type: "request_parameter"
              field_name: "offset"
        ```

        3.
        * fetches up to 5 records at a time by setting the "page_size" request param to 5
        * increments a page counter and set the request parameter "page" to the value of the counter
        ```
          paginator:
            type: "DefaultPaginator"
            page_size_option:
              inject_into: request_parameter
              field_name: page_size
            pagination_strategy:
              type: "PageIncrement"
              page_size: 5
            page_token_option:
              option_type: "request_parameter"
              field_name: "page"
        ```
    Attributes:
        page_size_option (Optional[RequestOption]): the request option to set the page size. Cannot be injected in the path.
        page_token_option (RequestOption): the request option to set the page token
        pagination_strategy (PaginationStrategy): Strategy defining how to get the next page token
        config (Config): connection config
        url_base (Union[InterpolatedString, str]): endpoint's base url
        decoder (Decoder): decoder to decode the response
    """

    page_size_option: Optional[RequestOption]
    page_token_option: RequestOption
    pagination_strategy: PaginationStrategy
    config: Config
    url_base: Union[InterpolatedString, str]
    options: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(options={})
    _token: Optional[Any] = field(init=False, repr=False, default=None)

    def __post_init__(self, options: Mapping[str, Any]):
        if self.page_size_option and self.page_size_option.inject_into == RequestOptionType.path:
            raise ValueError("page_size_option cannot be set in as path")
        if self.page_size_option and not self.pagination_strategy.get_page_size():
            raise ValueError("page_size_option cannot be set if the pagination strategy does not have a page_size")
        if self.pagination_strategy.get_page_size() and not self.page_size_option:
            raise ValueError("page_size_option must be set if the pagination strategy has a page_size")
        if isinstance(self.url_base, str):
            self.url_base = InterpolatedString(string=self.url_base, options=options)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        self._token = self.pagination_strategy.next_page_token(response, last_records)
        if self._token:
            return {"next_page_token": self._token}
        else:
            return None

    def path(self):
        if self._token and self.page_token_option.inject_into == RequestOptionType.path:
            # Replace url base to only return the path
            return str(self._token).replace(self.url_base.eval(self.config), "")
        else:
            return None

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return self._get_request_options(RequestOptionType.header)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_data)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_json)

    def reset(self):
        self.pagination_strategy.reset()

    def _get_request_options(self, option_type: RequestOptionType) -> Mapping[str, Any]:
        options = {}
        if self.page_token_option.inject_into == option_type:
            if option_type != RequestOptionType.path and self._token:
                options[self.page_token_option.field_name] = self._token
        if self.page_size_option and self.pagination_strategy.get_page_size() and self.page_size_option.inject_into == option_type:
            if option_type != RequestOptionType.path:
                options[self.page_size_option.field_name] = self.pagination_strategy.get_page_size()
        return options
