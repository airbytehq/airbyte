# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import calendar
from typing import Optional

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class ArticlesRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def articles_endpoint(cls, authenticator: Authenticator) -> "ArticlesRequestBuilder":
        return cls("d3v-airbyte", "help_center/incremental/articles").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._sort_by: Optional[str] = None
        self._sort_order: Optional[str] = None
        self._start_time: Optional[str] = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._sort_by:
            params["sort_by"] = self._sort_by
        if self._sort_order:
            params["sort_order"] = self._sort_order
        if self._start_time:
            params["start_time"] = self._start_time
        return params

    def with_sort_by(self, sort_by: str) -> "ArticlesRequestBuilder":
        self._sort_by = sort_by
        return self

    def with_sort_order(self, sort_order: str) -> "ArticlesRequestBuilder":
        self._sort_order = sort_order
        return self

    def with_start_time(self, start_time: pendulum.DateTime) -> "ArticlesRequestBuilder":
        self._start_time = str(calendar.timegm(start_time.timetuple()))
        return self
