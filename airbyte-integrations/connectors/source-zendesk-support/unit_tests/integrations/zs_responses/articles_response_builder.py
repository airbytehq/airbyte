# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from typing import Optional

from airbyte_cdk.connector_builder.models import HttpRequest
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from ..utils import http_request_to_str
from .pagination_strategies.next_page_pagination_strategy import NextPagePaginationStrategy


class ArticlesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def response(cls, next_page_url: Optional[HttpRequest] = None) -> "ArticlesResponseBuilder":
        return cls(
            find_template("articles", __file__), FieldPath("articles"), NextPagePaginationStrategy(http_request_to_str(next_page_url))
        )
