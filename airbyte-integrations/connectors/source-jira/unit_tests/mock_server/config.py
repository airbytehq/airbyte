# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict, List


class ConfigBuilder:
    """
    Builder for creating Jira connector configurations for tests.

    Example usage:
        config = (
            ConfigBuilder()
            .with_domain("mycompany.atlassian.net")
            .with_api_token("test_token")
            .with_projects(["PROJ1", "PROJ2"])
            .build()
        )
    """

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "api_token": "any_api_token",
            "domain": "airbyteio.atlassian.net",
            "email": "integration-test@airbyte.io",
            "start_date": "2021-01-01T00:00:00Z",
            "projects": [],
        }

    def with_api_token(self, api_token: str) -> "ConfigBuilder":
        """Set the API token for authentication."""
        self._config["api_token"] = api_token
        return self

    def with_domain(self, domain: str) -> "ConfigBuilder":
        """Set the Jira domain (e.g., 'mycompany.atlassian.net')."""
        self._config["domain"] = domain
        return self

    def with_email(self, email: str) -> "ConfigBuilder":
        """Set the email for authentication."""
        self._config["email"] = email
        return self

    def with_start_date(self, start_datetime: datetime) -> "ConfigBuilder":
        """Set the replication start date."""
        self._config["start_date"] = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def with_start_date_str(self, start_date: str) -> "ConfigBuilder":
        """Set the replication start date as a string."""
        self._config["start_date"] = start_date
        return self

    def with_projects(self, projects: List[str]) -> "ConfigBuilder":
        """Set the list of project keys to sync."""
        self._config["projects"] = projects
        return self

    def with_lookback_window_minutes(self, minutes: int) -> "ConfigBuilder":
        """Set the lookback window in minutes for incremental syncs."""
        self._config["lookback_window_minutes"] = minutes
        return self

    def with_enable_experimental_streams(self, enabled: bool) -> "ConfigBuilder":
        """Enable or disable experimental streams."""
        self._config["enable_experimental_streams"] = enabled
        return self

    def with_issues_stream_expand_with(self, expand_with: List[str]) -> "ConfigBuilder":
        """Set the expand options for the issues stream."""
        self._config["issues_stream_expand_with"] = expand_with
        return self

    def with_render_fields(self, render_fields: bool) -> "ConfigBuilder":
        """Enable or disable rendering of fields."""
        self._config["render_fields"] = render_fields
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the configuration dictionary."""
        return self._config
