# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "start_date": "2020-01-01T00:00:00.000Z",
            "credentials": {"auth_type": "token", "token": "test-token"},
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
