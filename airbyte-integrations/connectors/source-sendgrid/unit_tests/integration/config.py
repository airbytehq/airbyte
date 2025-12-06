# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, MutableMapping


# Constants for test data
API_KEY = "test_api_key_12345"
START_DATE = "2024-01-01T00:00:00Z"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "api_key": API_KEY,
            "start_date": START_DATE,
        }

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._config["api_key"] = api_key
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
