#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict


_API_KEY = "test_api_key_abc123"
_START_DATE = "2024-01-01T00:00:00Z"


class ConfigBuilder:
    """Builder for creating test configurations matching SendGrid spec."""

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "api_key": _API_KEY,
            "start_date": _START_DATE,
        }

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._config["api_key"] = api_key
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
