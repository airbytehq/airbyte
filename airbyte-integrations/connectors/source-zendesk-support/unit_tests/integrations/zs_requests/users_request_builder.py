# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import calendar
from typing import Optional

import pendulum

from .base_request_builder import ZendeskSupportBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class UsersRequestBuilder(ZendeskSupportBaseRequestBuilder):
    @classmethod
    def endpoint(cls, authenticator: Authenticator) -> "UsersRequestBuilder":
        return cls("d3v-airbyte", "incremental/users/cursor.json").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        super().__init__(subdomain, resource)
        self._start_time: Optional[str] = None
        self._cursor: Optional[str] = None
        self._include: Optional[str] = None

    @property
    def query_params(self):
        params = super().query_params or {}
        if self._start_time:
            params["start_time"] = self._start_time
        if self._cursor:
            params["cursor"] = self._cursor
        if self._include:
            params["include"] = self._include
        return params

    def with_start_time(self, start_time: pendulum.DateTime) -> "UsersRequestBuilder":
        self._start_time = str(calendar.timegm(start_time.timetuple()))
        return self

    def with_cursor(self, cursor: str) -> "UsersRequestBuilder":
        self._cursor = cursor
        return self

    def with_include(self, include: str) -> "UsersRequestBuilder":
        self._include = include
        return self
