#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class SendGridOffsetPaginationStrategy(PaginationStrategy):
    """Pagination strategy for SendGrid offset-based pagination (bounces, blocks, etc.)."""

    def __init__(self, page_size: int = 500):
        self._page_size = page_size

    def update(self, response: Dict[str, Any]) -> None:
        pass


class SendGridCursorPaginationStrategy(PaginationStrategy):
    """Pagination strategy for SendGrid cursor-based pagination (lists, singlesends, etc.)."""

    NEXT_PAGE_URL = "https://api.sendgrid.com/v3/marketing/lists?page_token=next_token&page_size=1000"

    def __init__(self, next_url: str = None):
        self._next_url = next_url or self.NEXT_PAGE_URL

    def update(self, response: Dict[str, Any]) -> None:
        response["_metadata"] = {"next": self._next_url}
