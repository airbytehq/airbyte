# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self):
        self._config = {
            "api_key": "test-api-key",
            "api_server": "us",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-02T00:00:00Z",
        }

    def build(self):
        return dict(self._config)
