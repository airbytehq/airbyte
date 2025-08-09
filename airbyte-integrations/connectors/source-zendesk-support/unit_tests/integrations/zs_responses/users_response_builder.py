# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from typing import Optional

from airbyte_cdk.connector_builder.models import HttpRequest
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from ..utils import http_request_to_str
from .pagination_strategies import EndOfStreamPaginationStrategy


class UsersResponseBuilder(HttpResponseBuilder):
    @classmethod
    def response(cls, url: Optional[HttpRequest] = None, cursor: Optional[str] = None) -> "UsersResponseBuilder":
        return cls(find_template("users", __file__), FieldPath("users"), EndOfStreamPaginationStrategy(http_request_to_str(url), cursor))

    @classmethod
    def identities_response(cls, url: Optional[HttpRequest] = None, cursor: Optional[str] = None) -> "UsersResponseBuilder":
        return cls(
            find_template("users", __file__), FieldPath("identities"), EndOfStreamPaginationStrategy(http_request_to_str(url), cursor)
        )
