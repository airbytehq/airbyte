# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from datetime import datetime
from typing import Any, Dict


class KlaviyoConfigBuilder:
    def __init__(self) -> None:
        self._config = {"api_key": "an_api_key", "start_date": "2021-01-01T00:00:00Z"}

    def with_start_date(self, start_date: datetime) -> "KlaviyoConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
