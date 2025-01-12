# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import CursorBasedPaginationStrategy


class GroupsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def groups_response(cls) -> "GroupsResponseBuilder":
        return cls(find_template("groups", __file__), FieldPath("groups"), CursorBasedPaginationStrategy())
