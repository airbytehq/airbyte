#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class PageIncrement(PaginationStrategy, JsonSchemaMixin):
    """
    Pagination strategy that returns the number of pages reads so far and returns it as the next page token

    Attributes:
        page_size (int): the number of records to request
        start_from_page (int): number of the initial page
    """

    page_size: int
    options: InitVar[Mapping[str, Any]]
    start_from_page: int = 0

    def __post_init__(self, options: Mapping[str, Any]):
        self._page = self.start_from_page

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        if len(last_records) < self.page_size:
            return None
        else:
            self._page += 1
            return self._page

    def reset(self):
        self._page = self.start_from_page

    def get_page_size(self) -> Optional[int]:
        return self.page_size
