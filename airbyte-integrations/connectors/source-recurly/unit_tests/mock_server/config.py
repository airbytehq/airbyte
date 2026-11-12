# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


BEGIN_TIME = "2025-01-01T00:00:00Z"
END_TIME = "2025-01-03T00:00:00Z"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {"api_key": "test-api-key", "begin_time": BEGIN_TIME, "end_time": "", "num_workers": 1}

    def with_begin_time(self, value: str) -> "ConfigBuilder":
        self._config["begin_time"] = value
        return self

    def with_end_time(self, value: str) -> "ConfigBuilder":
        self._config["end_time"] = value
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
