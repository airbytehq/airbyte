# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Optional


class ConfigBuilder:
    """
    Builder for creating Harvest connector configurations for tests.

    Example usage:
        config = (
            ConfigBuilder()
            .with_account_id("123456")
            .with_api_token("test_token_abc123")
            .with_replication_start_date(datetime(2024, 1, 1))
            .build()
        )
    """

    def __init__(self):
        self._account_id: Optional[str] = None
        self._api_token: Optional[str] = None
        self._start_date: Optional[str] = None

    def with_account_id(self, account_id: str) -> "ConfigBuilder":
        """Set the Harvest account ID."""
        self._account_id = account_id
        return self

    def with_api_token(self, api_token: str) -> "ConfigBuilder":
        """Set the API token for authentication."""
        self._api_token = api_token
        return self

    def with_replication_start_date(self, date: datetime) -> "ConfigBuilder":
        """Set the replication start date (for incremental syncs)."""
        self._start_date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def build(self) -> dict:
        """Build and return the configuration dictionary."""
        # Default start date if not provided
        start_date = self._start_date or "2021-01-01T00:00:00Z"

        config = {
            "account_id": self._account_id or "123456",
            "credentials": {"auth_type": "Token", "api_token": self._api_token or "test_token_abc123"},
            "replication_start_date": start_date,
        }

        return config
