# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def build(self):
        return {
            "api_key": "test-api-key",
            "api_server": "us",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-02T00:00:00Z",
        }
