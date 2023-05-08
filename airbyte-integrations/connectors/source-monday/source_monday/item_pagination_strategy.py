from typing import Any, Mapping, Optional, List, Tuple

from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


class ItemPaginationStrategy(PageIncrement):
    """
    Page increment strategy with subpages for the `items` stream.

    See Monday API documentation https://developer.monday.com/api-reference/docs.
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        # `self._page` corresponds to board page number
        # `self._sub_page` corresponds to item page number within its board
        self.start_from_page = 1
        self._page: Optional[int] = self.start_from_page
        self._sub_page: Optional[int] = self.start_from_page

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        Determines page and subpage numbers for the `items` stream

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        if len(last_records) >= self.page_size:
            self._sub_page += 1
        else:
            self._sub_page = self.start_from_page
            if len(response.json()["data"]["boards"]):
                self._page += 1
            else:
                return None

        return self._page, self._sub_page
