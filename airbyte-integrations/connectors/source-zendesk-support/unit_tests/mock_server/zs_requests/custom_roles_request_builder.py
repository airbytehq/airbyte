# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class CustomRolesRequestBuilder(ZendeskSupportBaseRequestBuilder):
    """
    Request builder for custom_roles stream.
    This stream uses CursorPagination with next_page (not links_next_paginator).
    """

    @classmethod
    def custom_roles_endpoint(cls, authenticator: Authenticator) -> "CustomRolesRequestBuilder":
        return cls("d3v-airbyte", "custom_roles").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)

    @property
    def query_params(self) -> Dict[str, Any]:
        return {}
