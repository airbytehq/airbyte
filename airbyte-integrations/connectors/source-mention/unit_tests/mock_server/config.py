# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-mention test configurations."""

    def __init__(self) -> None:
        self._api_key: str = "test-access-token"
        self._stats_start_date: str = "2026-09-01T00:00:00Z"

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._api_key = api_key
        return self

    def build(self) -> Dict[str, Any]:
        # Both fields are required by the Mention spec, so every config includes them.
        return {"api_key": self._api_key, "stats_start_date": self._stats_start_date}
