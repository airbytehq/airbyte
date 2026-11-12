# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest


class WaiteraidRequestBuilder:
    BASE_URL = "https://app.waiteraid.com"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {}

    @classmethod
    def search_booking_endpoint(cls, auth_hash: str, restid: str, date: str) -> "WaiteraidRequestBuilder":
        return (
            cls("/wa-api/searchBooking")
            .with_query_param("auth_hash", auth_hash)
            .with_query_param("restid", restid)
            .with_query_param("date", date)
        )

    def with_query_param(self, key: str, value: str) -> "WaiteraidRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"{self.BASE_URL}{self._path}", query_params=dict(self._query_params))
