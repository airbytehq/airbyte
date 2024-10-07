# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class TicketMetricsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def ticket_metrics_endpoint(cls, authenticator: Authenticator, ticket_id: int) -> "TicketMetricsRequestBuilder":
        return cls("d3v-airbyte", f"tickets/{ticket_id}/metrics").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)

    @property
    def query_params(self):
        return {}
