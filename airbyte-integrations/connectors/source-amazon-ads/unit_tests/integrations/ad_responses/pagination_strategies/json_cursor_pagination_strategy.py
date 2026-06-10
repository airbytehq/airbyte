# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


JSON_CURSOR_TOKEN = '{"key":"abc123"}'


class JsonCursorPaginationStrategy(PaginationStrategy):
    @staticmethod
    def update(response: Dict[str, Any]) -> None:
        response["cursorId"] = JSON_CURSOR_TOKEN
