# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict, List, Optional


class ConfigBuilder:
    """Builder class for creating LinkedIn Ads connector configurations."""

    def __init__(self):
        self._config: Dict[str, Any] = {
            "start_date": "2024-01-01",
            "credentials": {
                "auth_method": "access_token",
                "access_token": "test_access_token",
            },
            "account_ids": [],
            "lookback_window": 0,
            "ad_analytics_reports": [],
            "num_workers": 3,
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_access_token(self, access_token: str) -> "ConfigBuilder":
        self._config["credentials"] = {
            "auth_method": "access_token",
            "access_token": access_token,
        }
        return self

    def with_oauth2(self, client_id: str, client_secret: str, refresh_token: str) -> "ConfigBuilder":
        self._config["credentials"] = {
            "auth_method": "oAuth2.0",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
        return self

    def with_account_ids(self, account_ids: List[int]) -> "ConfigBuilder":
        self._config["account_ids"] = account_ids
        return self

    def with_lookback_window(self, lookback_window: int) -> "ConfigBuilder":
        self._config["lookback_window"] = lookback_window
        return self

    def with_ad_analytics_reports(self, reports: List[Dict[str, Any]]) -> "ConfigBuilder":
        self._config["ad_analytics_reports"] = reports
        return self

    def with_num_workers(self, num_workers: int) -> "ConfigBuilder":
        self._config["num_workers"] = num_workers
        return self

    def build(self) -> Dict[str, Any]:
        return self._config.copy()
