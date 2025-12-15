# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import NextPagePaginationStrategy


class CustomRolesResponseBuilder(HttpResponseBuilder):
    """
    Response builder for custom_roles stream.
    This stream uses CursorPagination with next_page (not links_next_paginator).
    """

    @classmethod
    def custom_roles_response(cls, next_page_url: Optional[str] = None) -> "CustomRolesResponseBuilder":
        return cls(
            find_template("custom_roles", __file__),
            FieldPath("custom_roles"),
            NextPagePaginationStrategy(next_page_url) if next_page_url else None,
        )
