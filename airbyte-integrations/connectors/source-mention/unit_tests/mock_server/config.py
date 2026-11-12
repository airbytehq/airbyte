# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self) -> None:
        self._api_key = "test_api_key"
        self._stats_start_date = "2026-09-01T00:00:00Z"

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._api_key = api_key
        return self

    def build(self) -> dict:
        return {"api_key": self._api_key, "stats_start_date": self._stats_start_date}
