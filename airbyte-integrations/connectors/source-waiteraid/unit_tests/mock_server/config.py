# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "auth_hash": "test-auth-hash",
            "restid": "1234",
            "start_date": "2026-09-01",
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
