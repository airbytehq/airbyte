# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Mapping

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
        self._sorting: Mapping[str, str] = {"sort_by": "updated_at"}

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._page_size:
            params["page[size]"] = self._page_size
        params.update(self._sorting)
        return params

    def with_page_size(self, page_size: int) -> "PostsRequestBuilder":
        self._page_size: int = page_size
        return self
