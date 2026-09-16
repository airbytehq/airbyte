# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-ashby test configurations."""

    def __init__(self) -> None:
        self._api_key: str = "test-api-key"
        self._start_date: str = "2024-01-01T00:00:00Z"

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._api_key = api_key
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        """Set `start_date`, which the spec requires in `YYYY-MM-DDTHH:MM:SSZ` format."""
        self._start_date = start_date
        return self

    def build(self) -> Dict[str, Any]:
        # Both fields are required by the Ashby spec, so every config includes them.
        return {"api_key": self._api_key, "start_date": self._start_date}
