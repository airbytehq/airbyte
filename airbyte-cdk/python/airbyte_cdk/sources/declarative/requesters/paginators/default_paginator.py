#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class DefaultPaginator(Paginator):
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
              type: RequestOption
              inject_into: request_parameter
              field_name: limit
            page_token_option:
              type: RequestPath
              path: "location"
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
              type: RequestOption
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
              type: RequestOption
              inject_into: request_parameter
              field_name: page_size
            pagination_strategy:
              type: "PageIncrement"
              page_size: 5
            page_token_option:
              type: RequestOption
              option_type: "request_parameter"
              field_name: "page"
        ```
    Attributes:
        page_size_option (Optional[RequestOption]): the request option to set the page size. Cannot be injected in the path.
        page_token_option (Optional[RequestPath, RequestOption]): the request option to set the page token
        pagination_strategy (PaginationStrategy): Strategy defining how to get the next page token
        config (Config): connection config
        url_base (Union[InterpolatedString, str]): endpoint's base url
        decoder (Decoder): decoder to decode the response
    """

    pagination_strategy: PaginationStrategy
    config: Config
    url_base: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})
    _token: Optional[Any] = field(init=False, repr=False, default=None)
    page_size_option: Optional[RequestOption] = None
    page_token_option: Optional[Union[RequestPath, RequestOption]] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        if self.page_size_option and not self.pagination_strategy.get_page_size():
            raise ValueError("page_size_option cannot be set if the pagination strategy does not have a page_size")
        if isinstance(self.url_base, str):
            self.url_base = InterpolatedString(string=self.url_base, parameters=parameters)

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Mapping[str, Any]]:
        self._token = self.pagination_strategy.next_page_token(response, last_records)
        if self._token:
            return {"next_page_token": self._token}
        else:
            return None

    def path(self):
        if self._token and self.page_token_option and isinstance(self.page_token_option, RequestPath):
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
        self._token = None

    def _get_request_options(self, option_type: RequestOptionType) -> Mapping[str, Any]:
        options = {}

        if (
            self.page_token_option
            and self._token
            and isinstance(self.page_token_option, RequestOption)
            and self.page_token_option.inject_into == option_type
        ):
            options[self.page_token_option.field_name] = self._token
        if self.page_size_option and self.pagination_strategy.get_page_size() and self.page_size_option.inject_into == option_type:
            options[self.page_size_option.field_name] = self.pagination_strategy.get_page_size()
        return options


class PaginatorTestReadDecorator(Paginator):
    """
    In some cases, we want to limit the number of requests that are made to the backend source. This class allows for limiting the number of
    pages that are queried throughout a read command.
    """

    _PAGE_COUNT_BEFORE_FIRST_NEXT_CALL = 1

    def __init__(self, decorated, maximum_number_of_pages: int = 5):
        if maximum_number_of_pages and maximum_number_of_pages < 1:
            raise ValueError(f"The maximum number of pages on a test read needs to be strictly positive. Got {maximum_number_of_pages}")
        self._maximum_number_of_pages = maximum_number_of_pages
        self._decorated = decorated
        self._page_count = self._PAGE_COUNT_BEFORE_FIRST_NEXT_CALL

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Mapping[str, Any]]:
        if self._page_count >= self._maximum_number_of_pages:
            return None

        self._page_count += 1
        return self._decorated.next_page_token(response, last_records)

    def path(self):
        return self._decorated.path()

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return self._decorated.get_request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

    def reset(self):
        self._decorated.reset()
        self._page_count = self._PAGE_COUNT_BEFORE_FIRST_NEXT_CALL
