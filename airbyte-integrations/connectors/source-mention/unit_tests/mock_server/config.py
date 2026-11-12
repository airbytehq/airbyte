# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self):
        self._config = {"api_key": "test-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}

    def with_api_key(self, api_key):
        self._config["api_key"] = api_key
        return self

    def build(self):
        return dict(self._config)
