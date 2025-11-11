#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.decoders import (
    Decoder,
    JsonDecoder,
    PaginationDecoderDecorator,
)
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import (
    PaginationStrategy,
)
from airbyte_cdk.sources.declarative.requesters.request_option import (
    RequestOption,
    RequestOptionType,
)
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils.mapping_helpers import (
    _validate_component_request_option_paths,
    get_interpolation_context,
)


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
    decoder: Decoder = field(
        default_factory=lambda: PaginationDecoderDecorator(decoder=JsonDecoder(parameters={}))
    )
    page_size_option: Optional[RequestOption] = None
    page_token_option: Optional[Union[RequestPath, RequestOption]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if self.page_size_option and not self.pagination_strategy.get_page_size():
            raise ValueError(
                "page_size_option cannot be set if the pagination strategy does not have a page_size"
            )
        if isinstance(self.url_base, str):
            self.url_base = InterpolatedString(string=self.url_base, parameters=parameters)

        if self.page_token_option and not isinstance(self.page_token_option, RequestPath):
            _validate_component_request_option_paths(
                self.config,
                self.page_size_option,
                self.page_token_option,
            )

    def get_initial_token(self) -> Optional[Any]:
        """
        Return the page token that should be used for the first request of a stream

        WARNING: get_initial_token() should not be used by streams that use RFR that perform checkpointing
        of state using page numbers. Because paginators are stateless
        """
        return self.pagination_strategy.initial_token

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any] = None,
    ) -> Optional[Mapping[str, Any]]:
        next_page_token = self.pagination_strategy.next_page_token(
            response=response,
            last_page_size=last_page_size,
            last_record=last_record,
            last_page_token_value=last_page_token_value,
        )
        if next_page_token:
            return {"next_page_token": next_page_token}
        else:
            return None

    def path(
        self,
        next_page_token: Optional[Mapping[str, Any]],
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Optional[str]:
        token = next_page_token.get("next_page_token") if next_page_token else None
        if token and self.page_token_option and isinstance(self.page_token_option, RequestPath):
            return str(token)
        else:
            return None

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter, next_page_token)

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return self._get_request_options(RequestOptionType.header, next_page_token)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_data, next_page_token)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_json, next_page_token)

    def _get_request_options(
        self, option_type: RequestOptionType, next_page_token: Optional[Mapping[str, Any]]
    ) -> MutableMapping[str, Any]:
        options: MutableMapping[str, Any] = {}

        token = next_page_token.get("next_page_token") if next_page_token else None
        if (
            self.page_token_option
            and token is not None
            and isinstance(self.page_token_option, RequestOption)
            and self.page_token_option.inject_into == option_type
        ):
            self.page_token_option.inject_into_request(options, token, self.config)

        if (
            self.page_size_option
            and self.pagination_strategy.get_page_size()
            and self.page_size_option.inject_into == option_type
        ):
            page_size = self.pagination_strategy.get_page_size()
            self.page_size_option.inject_into_request(options, page_size, self.config)

        return options


class PaginatorTestReadDecorator(Paginator):
    """
    In some cases, we want to limit the number of requests that are made to the backend source. This class allows for limiting the number of
    pages that are queried throughout a read command.

    WARNING: This decorator is not currently thread-safe like the rest of the low-code framework because it has
    an internal state to track the current number of pages counted so that it can exit early during a test read
    """

    _PAGE_COUNT_BEFORE_FIRST_NEXT_CALL = 1

    def __init__(self, decorated: Paginator, maximum_number_of_pages: int = 5) -> None:
        if maximum_number_of_pages and maximum_number_of_pages < 1:
            raise ValueError(
                f"The maximum number of pages on a test read needs to be strictly positive. Got {maximum_number_of_pages}"
            )
        self._maximum_number_of_pages = maximum_number_of_pages
        self._decorated = decorated
        self._page_count = self._PAGE_COUNT_BEFORE_FIRST_NEXT_CALL

    def get_initial_token(self) -> Optional[Any]:
        self._page_count = self._PAGE_COUNT_BEFORE_FIRST_NEXT_CALL
        return self._decorated.get_initial_token()

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any] = None,
    ) -> Optional[Mapping[str, Any]]:
        if self._page_count >= self._maximum_number_of_pages:
            return None

        self._page_count += 1
        return self._decorated.next_page_token(
            response, last_page_size, last_record, last_page_token_value
        )

    def path(
        self,
        next_page_token: Optional[Mapping[str, Any]],
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Optional[str]:
        return self._decorated.path(
            next_page_token=next_page_token,
            stream_state=stream_state,
            stream_slice=stream_slice,
        )

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_params(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return self._decorated.get_request_headers(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return self._decorated.get_request_body_data(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._decorated.get_request_body_json(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )
