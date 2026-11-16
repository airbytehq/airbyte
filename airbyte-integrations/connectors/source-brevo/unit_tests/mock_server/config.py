# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {"api_key": "test-api-key", "start_date": "2023-11-14T00:00:00Z"}

    def with_start_date(self, value: str) -> "ConfigBuilder":
        self._config["start_date"] = value
        return self

    def with_api_key(self, value: str) -> "ConfigBuilder":
        self._config["api_key"] = value
        return self

    def build(self) -> dict[str, str]:
        return dict(self._config)
