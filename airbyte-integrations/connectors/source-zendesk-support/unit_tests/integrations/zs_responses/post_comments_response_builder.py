# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import CursorBasedPaginationStrategy


class PostsCommentsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def posts_comments_response(cls) -> "PostsCommentsResponseBuilder":
        return cls(find_template("post_comments", __file__), FieldPath("comments"), CursorBasedPaginationStrategy())
