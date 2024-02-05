# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class GitHubPaginationStrategy(PaginationStrategy):
    @staticmethod
    def update(response: Dict[str, Any]) -> None:
        # headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=3>; rel="next"'},
        response["has_more"] = True
