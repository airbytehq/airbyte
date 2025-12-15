# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, find_template

from .pagination_strategies import NextPagePaginationStrategy


class SchedulesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def schedules_response(cls, next_page_url: Optional[str] = None) -> "SchedulesResponseBuilder":
        return cls(
            find_template("schedules", __file__),
            FieldPath("schedules"),
            NextPagePaginationStrategy(next_page_url) if next_page_url else None,
        )
