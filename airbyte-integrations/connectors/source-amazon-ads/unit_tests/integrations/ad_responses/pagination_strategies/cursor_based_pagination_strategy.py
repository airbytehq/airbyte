# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class CursorBasedPaginationStrategy(PaginationStrategy):
    @staticmethod
    def update(response: Dict[str, Any]) -> None:
        response["cursorId"] = "next-page-token"


class JsonCursorBasedPaginationStrategy(PaginationStrategy):
    """Simulates the real Amazon Attribution API which returns cursorId as a JSON-encoded string.

    This is the cursor format that triggers the bug fixed in the manifest:
    without the tojson filter, ast.literal_eval converts this JSON string
    into a Python dict, causing HTTP 400 errors on the next pagination request.
    """

    CURSOR_VALUE = '{"values":["B06ZYHXNCV#1",12738123158],"page":1,"version":"V2"}'

    @staticmethod
    def update(response: Dict[str, Any]) -> None:
        response["cursorId"] = JsonCursorBasedPaginationStrategy.CURSOR_VALUE
