# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from typing import Optional

from airbyte_cdk.connector_builder.models import HttpRequest
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from ..utils import http_request_to_str
from .pagination_strategies import CursorBasedPaginationStrategy


class PostsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def posts_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "PostsResponseBuilder":
        return cls(
            find_template("posts", __file__),
            FieldPath("posts"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )
