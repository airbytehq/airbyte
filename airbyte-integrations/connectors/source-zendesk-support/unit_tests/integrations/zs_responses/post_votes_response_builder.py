# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import CursorBasedPaginationStrategy


class PostsVotesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def posts_votes_response(cls) -> "PostsVotesResponseBuilder":
        return cls(find_template("votes", __file__), FieldPath("votes"), CursorBasedPaginationStrategy())
