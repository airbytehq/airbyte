#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Tuple
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


class ItemCursorPaginationStrategy(PageIncrement):
    """
    Page increment strategy with subpages for the `items` stream.

    From the `items` documentation https://developer.monday.com/api-reference/docs/items:
        Please note that you cannot return more than 100 items per query when using items at the root.
        To adjust your query, try only returning items on a specific board, nesting items inside a boards query,
        looping through the boards on your account, or querying less than 100 items at a time.

    This pagination strategy supports nested loop through `boards` on the top level and `items` on the second.
    See boards documentation for more details: https://developer.monday.com/api-reference/docs/boards#queries.
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        # `self._page` corresponds to board page number
        # `self._sub_page` corresponds to item page number within its board
        self.start_from_page = 1
        self._page: Optional[int] = self.start_from_page
        self._sub_page: Optional[int] = self.start_from_page

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        `items` stream use a separate 2 level pagination strategy where:
        1st level `boards` - incremental pagination
        2nd level `items_page` - cursor pagination

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        data = response.json()["body"]
        headers = data.get("headers", [])
        page_size = int(headers["X-Tracker-Pagination-Limit"])
        records_returned = int(headers["X-Tracker-Pagination-Returned"])
        current_offset = int(headers["X-Tracker-Pagination-Offset"])
        if "X-Tracker-Pagination-Total" not in headers:
            return self._page, None
        if records_returned < page_size:
            return self._page, None
        cursor = current_offset + page_size

        if cursor:
            return self._page, cursor
        else:
            self._page += 1
            return self._page, None
