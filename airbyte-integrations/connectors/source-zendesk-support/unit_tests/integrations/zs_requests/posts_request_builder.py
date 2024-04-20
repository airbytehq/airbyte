# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import calendar

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class PostsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def posts_endpoint(cls, authenticator: Authenticator) -> "PostsRequestBuilder":
        return cls("d3v-airbyte", "community/posts").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._start_time: int = None
        self._page_size: int = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._start_time:
            params["start_time"] = self._start_time
        if self._page_size:
            params["page[size]"] = self._page_size
        return params

    def with_start_time(self, start_time: int) -> "PostsRequestBuilder":
        self._start_time: int = calendar.timegm(pendulum.parse(start_time).utctimetuple())
        return self

    def with_page_size(self, page_size: int) -> "PostsRequestBuilder":
        self._page_size: int = page_size
        return self
