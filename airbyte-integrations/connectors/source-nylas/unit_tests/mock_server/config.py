# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def build(self) -> Dict[str, Any]:
        return {
            "api_key": "test-api-key",
            "api_server": "us",
            "start_date": "2026-09-01T00:00:00Z",
            "end_date": "2026-09-03T00:00:00Z",
        }
