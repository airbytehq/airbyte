# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class SlaPoliciesRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def sla_policies_endpoint(cls, authenticator: Authenticator) -> "SlaPoliciesRequestBuilder":
        return cls("d3v-airbyte", "slas/policies.json").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)

    @property
    def query_params(self) -> Dict[str, Any]:
        # sla_policies uses CursorPagination with next_page URL (RequestPath)
        # No pagination parameters in query string
        return {}
