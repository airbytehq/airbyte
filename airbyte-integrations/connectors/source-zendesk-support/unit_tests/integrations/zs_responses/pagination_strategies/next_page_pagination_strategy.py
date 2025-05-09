# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class NextPagePaginationStrategy(PaginationStrategy):
    def __init__(self, next_page_url: str) -> None:
        self._next_page_url = next_page_url

    def update(self, response: Dict[str, Any]) -> None:
        """
        Only allow for one page
        """
        response["next_page"] = self._next_page_url
