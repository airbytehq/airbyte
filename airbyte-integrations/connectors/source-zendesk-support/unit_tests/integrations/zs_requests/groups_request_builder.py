# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import calendar

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class GroupsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def groups_endpoint(cls, authenticator: Authenticator) -> "GroupsRequestBuilder":
        return cls("d3v-airbyte", "groups").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._page_size: int = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._page_size:
            params["per_page"] = self._page_size
        return params

    def with_page_size(self, page_size: int) -> "PostCommentVotesRequestBuilder":
        self._page_size: int = page_size
        return self
