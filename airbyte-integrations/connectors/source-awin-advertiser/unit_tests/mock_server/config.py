# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


ADVERTISER_ID = "12345"
API_KEY = "test-api-key"
BASE_URL = "https://api.awin.com"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "advertiserId": ADVERTISER_ID,
            "api_key": API_KEY,
            "step_increment": "P31D",
            "lookback_days": 0,
            "start_date": "2024-01-01",
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_lookback_days(self, lookback_days: int) -> "ConfigBuilder":
        self._config["lookback_days"] = lookback_days
        return self

    def with_regions(self, regions: list[str]) -> "ConfigBuilder":
        self._config["regions"] = regions
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
