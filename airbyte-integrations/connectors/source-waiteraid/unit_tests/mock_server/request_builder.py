# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class WaiteraidRequestBuilder:
    def __init__(self, path: str):
        self._path = path
        self._query_params = {}

    @classmethod
    def booking_endpoint(cls) -> "WaiteraidRequestBuilder":
        return cls("/wa-api/searchBooking")

    def with_query_param(self, key: str, value: str) -> "WaiteraidRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"https://app.waiteraid.com{self._path}", query_params=dict(self._query_params))
