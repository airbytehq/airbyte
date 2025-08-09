#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

from airbyte_cdk.test.mock_http.request import HttpRequest
from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


NEXT_PAGE_TOKEN = "New_Next_Page_Token"


class RechargePaginationStrategy(PaginationStrategy):
    def __init__(self, request: HttpRequest, next_page_token: str) -> None:
        self._next_page_token = next_page_token

    def update(self, response: Dict[str, Any]) -> None:
        response["next_cursor"] = self._next_page_token
