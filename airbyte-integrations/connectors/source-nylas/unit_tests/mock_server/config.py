# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-nylas test configurations. All four fields are required by the spec."""

    def __init__(self) -> None:
        self._api_key = "test-api-key"
        self._api_server = "us"
        self._start_date = "2026-09-01T00:00:00Z"
        self._end_date = "2026-09-03T00:00:00Z"

    def build(self) -> Dict[str, Any]:
        return {
            "api_key": self._api_key,
            "api_server": self._api_server,
            "start_date": self._start_date,
            "end_date": self._end_date,
        }
