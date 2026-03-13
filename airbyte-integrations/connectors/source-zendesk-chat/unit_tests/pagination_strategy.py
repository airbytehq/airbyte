# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class ZendeskChatPaginationStrategy(PaginationStrategy):
    def __init__(self, entry_field: str, next_page_url: str):
        self._entry_field = entry_field
        self._next_page_url = next_page_url

    def update(self, response: Dict[str, Any]) -> None:
        response["count"] = 1000
        response["next_page"] = self._next_page_url
