# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Optional


class ConfigBuilder:
    def __init__(self):
        self._customer_id = "1234567890"
        self._developer_token = "test_developer_token"
        self._client_id = "test_client_id"
        self._client_secret = "test_client_secret"
        self._refresh_token = "test_refresh_token"
        self._start_date = "2024-01-01"
        self._end_date: Optional[str] = None
        self._conversion_window_days = 14
        self._custom_queries_array = []

    def with_customer_id(self, customer_id: str) -> "ConfigBuilder":
        self._customer_id = customer_id
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def with_end_date(self, end_date: str) -> "ConfigBuilder":
        self._end_date = end_date
        return self

    def with_conversion_window_days(self, days: int) -> "ConfigBuilder":
        self._conversion_window_days = days
        return self

    def with_custom_queries(self, queries: list) -> "ConfigBuilder":
        self._custom_queries_array = queries
        return self

    def build(self) -> dict:
        config = {
            "credentials": {
                "developer_token": self._developer_token,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
            },
            "customer_id": self._customer_id,
            "start_date": self._start_date,
            "conversion_window_days": self._conversion_window_days,
            "custom_queries_array": self._custom_queries_array,
        }
        if self._end_date:
            config["end_date"] = self._end_date
        return config
