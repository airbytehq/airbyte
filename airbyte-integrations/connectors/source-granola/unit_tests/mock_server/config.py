# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional


class ConfigBuilder:
    """Builder for source-granola test configurations."""

    def __init__(self) -> None:
        self._api_key: str = "test-api-key"
        self._start_date: Optional[str] = None

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._api_key = api_key
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        """Set `start_date`, which the spec documents in `YYYY-MM-DD` format."""
        self._start_date = start_date
        return self

    def build(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {"api_key": self._api_key}
        if self._start_date:
            config["start_date"] = self._start_date
        return config
