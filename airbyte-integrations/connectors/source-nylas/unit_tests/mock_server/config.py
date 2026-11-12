# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def build(self):
        return {
            "api_key": "test-api-key",
            "api_server": "us",
            "start_date": "2026-09-01T00:00:00Z",
            "end_date": "2026-09-03T00:00:00Z",
        }
