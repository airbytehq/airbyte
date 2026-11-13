# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-revenuecat test configurations."""

    def __init__(self) -> None:
        self._api_key: str = "sk_test_key"
        self._start_date: str = "2024-01-01T00:00:00Z"

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return {"api_key": self._api_key, "start_date": self._start_date}
