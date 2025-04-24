# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import calendar

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class TicketFormsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def ticket_forms_endpoint(cls, authenticator: Authenticator) -> "TicketFormsRequestBuilder":
        return cls("d3v-airbyte", "ticket_forms").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._start_time: int = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._start_time:
            params["start_time"] = self._start_time
        return params

    def with_start_time(self, start_time: int) -> "TicketFormsRequestBuilder":
        self._start_time: int = calendar.timegm(pendulum.parse(start_time).utctimetuple())
        return self
