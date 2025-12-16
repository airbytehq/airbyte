# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import NextPagePaginationStrategy


class SlaPoliciesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def sla_policies_response(cls, next_page_url: Optional[str] = None) -> "SlaPoliciesResponseBuilder":
        return cls(
            find_template("sla_policies", __file__),
            FieldPath("sla_policies"),
            NextPagePaginationStrategy(next_page_url) if next_page_url else None,
        )
