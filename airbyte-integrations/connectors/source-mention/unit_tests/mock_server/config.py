# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


API_KEY = "test-mention-token"


class ConfigBuilder:
    """Builder for source-mention test configurations."""

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {"api_key": API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
