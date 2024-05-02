#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


@dataclass
class CustomPaging(PageIncrement):

    def next_page_token(self, response: requests.Response) -> Optional[Any]:
        headers = response.json().get("headers")
        if "X-Tracker-Pagination-Total" not in headers:
            return None  # not paginating
        page_size = int(headers["X-Tracker-Pagination-Limit"])
        records_returned = int(headers["X-Tracker-Pagination-Returned"])
        current_offset = int(headers["X-Tracker-Pagination-Offset"])

        if records_returned < page_size:
            return None  # no more
        return current_offset + page_size

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._page = 1

    def reset(self):
        self._page = 1
