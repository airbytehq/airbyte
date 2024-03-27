# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class MyPaginationStrategy(PaginationStrategy):
    """
    Pagination strategy that returns the number of records reads so far and returns it as the next page token
    Examples:
        # page_size to be a constant integer value
        pagination_strategy:
          type: OffsetIncrement
          page_size: 2

        # page_size to be a constant string value
        pagination_strategy:
          type: OffsetIncrement
          page_size: "2"

        # page_size to be an interpolated string value
        pagination_strategy:
          type: OffsetIncrement
          page_size: "{{ parameters['items_per_page'] }}"

    Attributes:
        page_size (InterpolatedString): the number of records to request


type: DefaultPaginator
page_size_options:
  type: RequestOption
  field_name: count
  inject_into: request_parameter
page_token_option:
  type: RequestOption
  field_name: startIndex
  inject_into: request_parameter
pagination_strategy:
  type: CustomPaginationStrategy
  class_name: source_amazon_ads.components.MyPaginationStrategy

    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.page_size: Optional[Union[str, int]] = 10
        self.decoder: Decoder = JsonDecoder(parameters={})
        self.inject_on_first_request: bool = False
        self._offset = 0
        page_size = str(self.page_size) if isinstance(self.page_size, int) else self.page_size
        if page_size:
            self._page_size = InterpolatedString(page_size, parameters=parameters)
        else:
            self._page_size = None

    @property
    def initial_token(self) -> Optional[Any]:
        if self.inject_on_first_request:
            return self._offset
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (self._page_size and len(last_records) < self._page_size.eval(self.config, response=decoded_response)) or len(last_records) == 0:
            return None
        else:
            self._offset += len(last_records)
            return self._offset

    def reset(self):
        self._offset = 0

    def get_page_size(self) -> Optional[int]:
        if self._page_size:
            page_size = self._page_size.eval(self.config)
            if not isinstance(page_size, int):
                raise Exception(f"{page_size} is of type {type(page_size)}. Expected {int}")
            return page_size
        else:
            return self._page_size
