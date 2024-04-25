# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class HubspotPaginationStrategy(PaginationStrategy):
    NEXT_PAGE_TOKEN = {"after": "256"}

    def update(self, response: Dict[str, Any]) -> None:
        response["paging"] = {
            "next": {
                "link": "link_to_the_next_page",
                **self.NEXT_PAGE_TOKEN
            },
            "prev": {
                "before": None,
                "link": None
            }
        }
