# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for creating test configurations"""

    def __init__(self):
        self._config: Dict[str, Any] = {
            "auth_token": "test_token_abc123",
            "hostname": "sentry.io",
            "organization": "test-org",
            "project": "test-project",
        }

    def with_auth_token(self, token: str) -> "ConfigBuilder":
        self._config["auth_token"] = token
        return self

    def with_organization(self, org: str) -> "ConfigBuilder":
        self._config["organization"] = org
        return self

    def with_project(self, project: str) -> "ConfigBuilder":
        self._config["project"] = project
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
