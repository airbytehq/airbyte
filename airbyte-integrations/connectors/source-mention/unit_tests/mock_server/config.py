# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "api_key": "test_api_key",
            "stats_start_date": "2026-09-01T00:00:00Z",
        }

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._config["api_key"] = api_key
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
