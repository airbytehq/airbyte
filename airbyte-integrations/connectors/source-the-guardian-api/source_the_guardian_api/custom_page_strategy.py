#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


@dataclass
class CustomPageIncrement(PageIncrement):
    """
    Starts page from 1 instead of the default value that is 0. Stops Pagination when currentPage is equal to totalPages.
    """

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        res = response.json().get("response")
        currPage = res.get("currentPage")
        totalPages = res.get("pages")
        if currPage < totalPages:
            self._page += 1
            return self._page
        else:
            return None

    def __post_init__(self, options: Mapping[str, Any]):
        self._page = 1

    def reset(self):
        self._page = 1
