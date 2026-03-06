# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import List, Optional


class ConfigBuilder:
    """
    Builder for creating Google Search Console connector configurations for tests.

    Example usage:
        config = (
            ConfigBuilder()
            .with_site_urls(["https://example.com/"])
            .with_start_date("2024-01-01")
            .with_end_date("2024-01-31")
            .with_oauth_credentials("client_id", "client_secret", "refresh_token")
            .build()
        )
    """

    def __init__(self):
        self._site_urls: List[str] = ["https://example.com/"]
        self._start_date: str = "2021-01-01"
        self._end_date: Optional[str] = None
        self._auth_type: str = "Client"
        self._client_id: str = "test_client_id"
        self._client_secret: str = "test_client_secret"
        self._refresh_token: str = "test_refresh_token"
        self._access_token: Optional[str] = None
        self._service_account_info: Optional[str] = None
        self._email: Optional[str] = None
        self._custom_reports_array: Optional[List[dict]] = None
        self._data_state: str = "final"
        self._always_use_aggregation_type_auto: bool = False

    def with_site_urls(self, site_urls: List[str]) -> "ConfigBuilder":
        """Set the site URLs to sync."""
        self._site_urls = site_urls
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        """Set the start date for data replication (format: YYYY-MM-DD)."""
        self._start_date = start_date
        return self

    def with_end_date(self, end_date: str) -> "ConfigBuilder":
        """Set the end date for data replication (format: YYYY-MM-DD)."""
        self._end_date = end_date
        return self

    def with_oauth_credentials(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        access_token: Optional[str] = None,
    ) -> "ConfigBuilder":
        """Set OAuth credentials for authentication."""
        self._auth_type = "Client"
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token = access_token
        return self

    def with_service_account_credentials(
        self,
        service_account_info: str,
        email: str,
    ) -> "ConfigBuilder":
        """Set Service Account credentials for authentication."""
        self._auth_type = "Service"
        self._service_account_info = service_account_info
        self._email = email
        return self

    def with_custom_reports(self, custom_reports: List[dict]) -> "ConfigBuilder":
        """Set custom reports configuration."""
        self._custom_reports_array = custom_reports
        return self

    def with_data_state(self, data_state: str) -> "ConfigBuilder":
        """Set data freshness (final or all)."""
        self._data_state = data_state
        return self

    def with_always_use_aggregation_type_auto(self, value: bool) -> "ConfigBuilder":
        """Set whether to always use aggregationType=auto."""
        self._always_use_aggregation_type_auto = value
        return self

    def build(self) -> dict:
        """Build and return the configuration dictionary."""
        config = {
            "site_urls": self._site_urls,
            "start_date": self._start_date,
            "data_state": self._data_state,
            "always_use_aggregation_type_auto": self._always_use_aggregation_type_auto,
        }

        if self._end_date:
            config["end_date"] = self._end_date

        if self._auth_type == "Client":
            config["authorization"] = {
                "auth_type": "Client",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
            }
            if self._access_token:
                config["authorization"]["access_token"] = self._access_token
        else:
            config["authorization"] = {
                "auth_type": "Service",
                "service_account_info": self._service_account_info,
                "email": self._email,
            }

        if self._custom_reports_array:
            config["custom_reports_array"] = self._custom_reports_array

        return config
