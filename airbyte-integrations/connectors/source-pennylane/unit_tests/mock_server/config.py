# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {"api_key": "test-api-key", "start_time": "2024-01-01T00:00:00Z"}

    def with_start_time(self, start_time: str) -> "ConfigBuilder":
        self._config["start_time"] = start_time
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
