# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import calendar
from typing import Optional

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class PostsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def posts_endpoint(cls, authenticator: Authenticator) -> "PostsRequestBuilder":
        return cls("d3v-airbyte", "community/posts").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._start_time: Optional[int] = None
        self._page_size: Optional[int] = None
        self._after_cursor: Optional[str] = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._start_time is not None:
            params["start_time"] = self._start_time
        if self._page_size is not None:
            params["page[size]"] = self._page_size
        if self._after_cursor is not None:
            params["page[after]"] = self._after_cursor
        return params

    def with_start_time(self, start_time: str) -> "PostsRequestBuilder":
        self._start_time: int = calendar.timegm(pendulum.parse(start_time).utctimetuple())
        return self

    def with_page_size(self, page_size: int) -> "PostsRequestBuilder":
        self._page_size: int = page_size
        return self

    def with_after_cursor(self, after_cursor: str) -> "PostsRequestBuilder":
        self._after_cursor: str = after_cursor
        return self
