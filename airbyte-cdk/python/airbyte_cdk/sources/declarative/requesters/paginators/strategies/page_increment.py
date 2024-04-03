#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.types import Config, Record


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
        self._page = self.start_from_page
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
            return self._page
        return None

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Any]:
        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (self._page_size and len(last_records) < self._page_size) or len(last_records) == 0:
            return None
        else:
            self._page += 1
            return self._page

    def reset(self) -> None:
        self._page = self.start_from_page

    def get_page_size(self) -> Optional[int]:
        return self._page_size
