# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {"apikey": "test-api-key"}

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._config["apikey"] = api_key
        return self

    def with_query(self, stream: str, query: str) -> "ConfigBuilder":
        self._config[f"query_{stream}"] = query
        return self

    def build(self) -> dict:
        return dict(self._config)
