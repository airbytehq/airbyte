# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class CountBasedPaginationStrategy(PaginationStrategy):
    @staticmethod
    def update(response: List[Dict[str, Any]]) -> None:
        if len(response) < 100:
            response.extend([response.pop()] * (100 - len(response)))
        elif len(response) > 100:
            response_page = response[:100]
            response.clear()
            response.extend(response_page)
        else:
            pass
