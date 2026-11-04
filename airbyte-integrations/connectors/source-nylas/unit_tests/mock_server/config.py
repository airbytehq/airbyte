# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional


class ConfigBuilder:
    """Builder for source-nylas test configurations."""

    def __init__(self) -> None:
        self._api_key = "test_key"
        self._api_server = "us"
        self._start_date: Optional[str] = None
        self._end_date: Optional[str] = None

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._api_key = api_key
        return self

    def with_api_server(self, api_server: str) -> "ConfigBuilder":
        self._api_server = api_server
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def with_end_date(self, end_date: str) -> "ConfigBuilder":
        self._end_date = end_date
        return self

    def build(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {"api_key": self._api_key, "api_server": self._api_server}
        if self._start_date:
            config["start_date"] = self._start_date
        if self._end_date:
            config["end_date"] = self._end_date
        return config
