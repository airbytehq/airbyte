# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class EndOfStreamPaginationStrategy(PaginationStrategy):
    def __init__(self, url: str, cursor) -> None:
        self._next_page_url = url
        self._cursor = cursor

    def update(self, response: Dict[str, Any]) -> None:
        """
        Only allow for one page
        """
        response["after_url"] = f"{self._next_page_url}?cursor={self._cursor}"
        response["after_cursor"] = self._cursor
        response["end_of_stream"] = False
