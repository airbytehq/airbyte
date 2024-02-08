# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import CursorBasedPaginationStrategy


class TicketFormsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_forms_response(cls) -> "TicketFormsResponseBuilder":
        return cls(find_template("ticket_forms", __file__), FieldPath("ticket_forms"), CursorBasedPaginationStrategy())
