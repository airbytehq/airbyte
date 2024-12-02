# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import calendar

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class TicketsRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def tickets_endpoint(cls, authenticator: Authenticator) -> "TicketsRequestBuilder":
        return cls("d3v-airbyte", "incremental/tickets/cursor.json").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._start_time: int = None
        self._cursor: str = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._cursor:
            params["cursor"] = self._cursor
            return params
        if self._start_time:
            params["start_time"] = self._start_time
        return params

    def with_start_time(self, start_time: int) -> "TicketsRequestBuilder":
        self._start_time: int = start_time
        return self

    def with_cursor(self, cursor: str) -> "TicketsRequestBuilder":
        self._cursor = cursor
        return self
