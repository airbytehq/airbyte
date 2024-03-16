from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class WebAnalyticsPaginationStrategy(PaginationStrategy):
    NEXT_PAGE_TOKEN = {"after": "this_page_last_record_id"}

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
