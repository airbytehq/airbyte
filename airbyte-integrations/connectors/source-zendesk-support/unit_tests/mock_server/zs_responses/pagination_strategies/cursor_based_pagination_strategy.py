# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class CursorBasedPaginationStrategy(PaginationStrategy):
    def __init__(self, first_url: Optional[str] = None) -> None:
        self._first_url = first_url

    def update(self, response: Dict[str, Any]) -> None:
        """
        Only allow for one page
        """
        response["meta"]["has_more"] = True
        response["meta"]["after_cursor"] = "after-cursor"
        response["meta"]["before_cursor"] = "before-cursor"
        if self._first_url:
            response["links"]["next"] = (
                self._first_url + "&page[after]=after-cursor" if "?" in self._first_url else self._first_url + "?page[after]=after-cursor"
            )
