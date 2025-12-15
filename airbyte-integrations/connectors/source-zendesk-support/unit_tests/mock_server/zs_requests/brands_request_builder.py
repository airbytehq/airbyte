# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class BrandsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def brands_endpoint(cls, authenticator: Authenticator) -> "BrandsRequestBuilder":
        return cls("d3v-airbyte", "brands").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._page_size: Optional[int] = None
        self._after_cursor: Optional[str] = None

    @property
    def query_params(self) -> Dict[str, Any]:
        params = {}
        if self._page_size is not None:
            params["page[size]"] = self._page_size
        if self._after_cursor is not None:
            params["page[after]"] = self._after_cursor
        return params

    def with_page_size(self, page_size: int) -> "BrandsRequestBuilder":
        self._page_size = page_size
        return self

    def with_after_cursor(self, after_cursor: str) -> "BrandsRequestBuilder":
        self._after_cursor = after_cursor
        return self
