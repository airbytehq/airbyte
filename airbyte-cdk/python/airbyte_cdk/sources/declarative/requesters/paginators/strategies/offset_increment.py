#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.types import Config, Record


@dataclass
class OffsetIncrement(PaginationStrategy):
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
    """

    config: Config
    page_size: Optional[Union[str, int]]
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))
    inject_on_first_request: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._offset = 0
        page_size = str(self.page_size) if isinstance(self.page_size, int) else self.page_size
        if page_size:
            self._page_size: Optional[InterpolatedString] = InterpolatedString(page_size, parameters=parameters)
        else:
            self._page_size = None

    @property
    def initial_token(self) -> Optional[Any]:
        if self.inject_on_first_request:
            return self._offset
        return None

    def next_page_token(self, response: requests.Response, last_page_size: int, last_record: Optional[Record]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)

        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (self._page_size and last_page_size < self._page_size.eval(self.config, response=decoded_response)) or last_page_size == 0:
            return None
        else:
            self._offset += last_page_size
            return self._offset

    def reset(self, reset_value: Optional[Any] = 0) -> None:
        if not isinstance(reset_value, int):
            raise ValueError(f"Reset value {reset_value} for OffsetIncrement pagination strategy was not an integer")
        else:
            self._offset = reset_value

    def get_page_size(self) -> Optional[int]:
        if self._page_size:
            page_size = self._page_size.eval(self.config)
            if not isinstance(page_size, int):
                raise Exception(f"{page_size} is of type {type(page_size)}. Expected {int}")
            return page_size
        else:
            return None
