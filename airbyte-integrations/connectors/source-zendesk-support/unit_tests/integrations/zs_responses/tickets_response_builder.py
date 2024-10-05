# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import CursorBasedPaginationStrategy


class TicketsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def tickets_response(cls) -> "TicketsResponseBuilder":
        return cls(find_template("tickets", __file__), FieldPath("tickets"), CursorBasedPaginationStrategy())
