# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-nylas test configurations."""

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "api_key": "test-api-key",
            "api_server": "us",
            "start_date": "2026-09-01T00:00:00Z",
            "end_date": "2026-09-03T00:00:00Z",
        }

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
