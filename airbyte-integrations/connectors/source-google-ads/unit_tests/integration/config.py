# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import date
from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "credentials": {
                "developer_token": "test_token",
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "refresh_token": "test_refresh_token",
            },
            "customer_id": "1234567890",
            "start_date": "2023-09-04",
            "conversion_window_days": 14,
            "custom_queries_array": []
        }

    def with_start_date(self, start_date: date) -> "ConfigBuilder":
        self._config["start_date"] = start_date.isoformat()
        return self

    def with_conversion_window_days(self, conversion_window_days: int) -> "ConfigBuilder":
        self._config["conversion_window_days"] = conversion_window_days
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
