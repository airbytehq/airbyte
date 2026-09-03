# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict, Optional


class ConfigBuilder:
    """
    Builder for creating Klaviyo connector configurations for tests.

    Example usage:
        config = (
            ConfigBuilder()
            .with_api_key("test_api_key")
            .with_start_date(datetime(2024, 1, 1))
            .build()
        )
    """

    def __init__(self):
        self._api_key: Optional[str] = None
        self._start_date: Optional[str] = None
        self._disable_fetching_predictive_analytics: bool = False
        self._num_workers: int = 10
        self._event_metric_ids: Optional[str] = None
        self._reporting_lookback_window: Optional[int] = None

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        """Set the Klaviyo API key."""
        self._api_key = api_key
        return self

    def with_start_date(self, date: datetime) -> "ConfigBuilder":
        """Set the replication start date (for incremental syncs)."""
        self._start_date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def with_start_date_str(self, date_str: str) -> "ConfigBuilder":
        """Set the replication start date as a string."""
        self._start_date = date_str
        return self

    def with_disable_fetching_predictive_analytics(self, disable: bool = True) -> "ConfigBuilder":
        """Disable fetching predictive analytics for profiles stream."""
        self._disable_fetching_predictive_analytics = disable
        return self

    def with_event_metric_ids(self, event_metric_ids: str) -> "ConfigBuilder":
        """Set the comma-separated metric IDs used to filter the events and events_detailed streams."""
        self._event_metric_ids = event_metric_ids
        return self

    def with_reporting_lookback_window(self, days: int) -> "ConfigBuilder":
        """Set the number of days the flow_series_reports stream re-syncs on every incremental run."""
        self._reporting_lookback_window = days
        return self

    def with_num_workers(self, num_workers: int) -> "ConfigBuilder":
        """Set the number of concurrent threads."""
        self._num_workers = num_workers
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the configuration dictionary."""
        start_date = self._start_date or "2012-01-01T00:00:00Z"

        config = {
            "api_key": self._api_key or "test_api_key_abc123",
            "start_date": start_date,
            "disable_fetching_predictive_analytics": self._disable_fetching_predictive_analytics,
            "num_workers": self._num_workers,
        }

        if self._event_metric_ids is not None:
            config["event_metric_ids"] = self._event_metric_ids

        if self._reporting_lookback_window is not None:
            config["reporting_lookback_window"] = self._reporting_lookback_window

        return config
