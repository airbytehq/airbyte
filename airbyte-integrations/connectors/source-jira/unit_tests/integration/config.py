# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict, List, Optional


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "api_token": "any_api_token",
            "domain": "airbyteio.atlassian.net",
            "email": "integration-test@airbyte.io",
            "start_date": "2021-01-01T00:00:00Z",
            "projects": [],
        }

    def with_api_token(self, api_token: str) -> "ConfigBuilder":
        self._config["api_token"] = api_token
        return self

    def with_domain(self, domain: str) -> "ConfigBuilder":
        self._config["domain"] = domain
        return self

    def with_email(self, email: str) -> "ConfigBuilder":
        self._config["email"] = email
        return self

    def with_start_date(self, start_datetime: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def with_start_date_str(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_projects(self, projects: List[str]) -> "ConfigBuilder":
        self._config["projects"] = projects
        return self

    def with_enable_experimental_streams(self, enabled: bool = True) -> "ConfigBuilder":
        self._config["enable_experimental_streams"] = enabled
        return self

    def with_lookback_window_minutes(self, minutes: Optional[int]) -> "ConfigBuilder":
        if minutes is not None:
            self._config["lookback_window_minutes"] = minutes
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
