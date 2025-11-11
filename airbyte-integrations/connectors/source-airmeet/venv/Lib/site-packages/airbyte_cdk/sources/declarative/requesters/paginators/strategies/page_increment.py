#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import (
    PaginationStrategy,
)
from airbyte_cdk.sources.types import Config, Record


@dataclass
class PageIncrement(PaginationStrategy):
    """
    Pagination strategy that returns the number of pages reads so far and returns it as the next page token

    Attributes:
        page_size (int): the number of records to request
        start_from_page (int): number of the initial page
    """

    config: Config
    page_size: Optional[Union[str, int]]
    parameters: InitVar[Mapping[str, Any]]
    start_from_page: int = 0
    inject_on_first_request: bool = False

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if isinstance(self.page_size, int) or (self.page_size is None):
            self._page_size = self.page_size
        else:
            page_size = InterpolatedString(self.page_size, parameters=parameters).eval(self.config)
            if not isinstance(page_size, int):
                raise Exception(f"{page_size} is of type {type(page_size)}. Expected {int}")
            self._page_size = page_size

    @property
    def initial_token(self) -> Optional[Any]:
        if self.inject_on_first_request:
            return self.start_from_page
        return None

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any],
    ) -> Optional[Any]:
        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (self._page_size and last_page_size < self._page_size) or last_page_size == 0:
            return None
        elif last_page_token_value is None:
            # If the PageIncrement strategy does not inject on the first request, the incoming last_page_token_value
            # may be None. When this is the case, we assume we've already requested the first page specified by
            # start_from_page and must now get the next page
            return self.start_from_page + 1
        elif not isinstance(last_page_token_value, int):
            raise ValueError(
                f"Last page token value {last_page_token_value} for PageIncrement pagination strategy was not an integer"
            )
        else:
            return last_page_token_value + 1

    def get_page_size(self) -> Optional[int]:
        return self._page_size
