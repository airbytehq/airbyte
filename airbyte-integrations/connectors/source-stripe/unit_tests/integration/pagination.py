# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class StripePaginationStrategy(PaginationStrategy):
    @staticmethod
    def update(response: Dict[str, Any]) -> None:
        response["has_more"] = True
