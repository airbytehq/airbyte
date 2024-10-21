# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import CursorBasedPaginationStrategy


class PostsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def posts_response(cls) -> "PostsResponseBuilder":
        return cls(find_template("posts", __file__), FieldPath("posts"), CursorBasedPaginationStrategy())
