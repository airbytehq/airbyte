# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict, List


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "credentials": {"option_title": "PAT Credentials", "personal_access_token": "GITHUB_TEST_TOKEN"},
            "start_date": "2020-05-01T00:00:00Z",
        }

    def with_repositories(self, repositories: List[str]) -> "ConfigBuilder":
        self._config["repositories"] = repositories
        return self

    def with_client_secret(self, client_secret: str) -> "ConfigBuilder":
        self._config["client_secret"] = client_secret
        return self

    def with_start_date(self, start_datetime: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_datetime.isoformat()[:-13] + "Z"
        return self

    def with_branches(self, branches: List[str]) -> "ConfigBuilder":
        self._config["branches"] = branches
        return self

    def with_api_url(self, api_url: str) -> "ConfigBuilder":
        self._config["api_url"] = api_url
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
