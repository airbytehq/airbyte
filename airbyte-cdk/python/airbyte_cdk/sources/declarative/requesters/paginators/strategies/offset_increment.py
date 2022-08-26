#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.pagination_strategy import PaginationStrategy


class OffsetIncrement(PaginationStrategy):
    """
    Pagination strategy that returns the number of records reads so far and returns it as the next page token
    """

    def __init__(self, page_size: int):
        """
        :param page_size: the number of records to request
        """
        self._offset = 0
        self._page_size = page_size

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        if len(last_records) < self._page_size:
            return None
        else:
            self._offset += len(last_records)
            return self._offset
