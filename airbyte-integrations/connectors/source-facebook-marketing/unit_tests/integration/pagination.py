#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict
from urllib.parse import urlunparse

from airbyte_cdk.test.mock_http.request import HttpRequest
from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


NEXT_PAGE_TOKEN = "QVFIUlhOX3Rnbm5Y"


class FacebookMarketingPaginationStrategy(PaginationStrategy):
    def __init__(self, request: HttpRequest, next_page_token: str) -> None:
        self._next_page_token = next_page_token
        self._next_page_url = f"{urlunparse(request._parsed_url)}&after={self._next_page_token}"

    def update(self, response: Dict[str, Any]) -> None:
        # set a constant value for paging.cursors.after so we know how the 'next' link is built
        # https://developers.facebook.com/docs/graph-api/results
        response["paging"]["cursors"]["after"] = self._next_page_token
        response["paging"]["next"] = self._next_page_url
