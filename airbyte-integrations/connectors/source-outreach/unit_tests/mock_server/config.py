# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


START_DATE = "2020-11-16T00:00:00Z"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
            "redirect_uri": "https://example.com/callback",
            "start_date": START_DATE,
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_num_workers(self, num_workers: int) -> "ConfigBuilder":
        self._config["num_workers"] = num_workers
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
