# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


class ConfigBuilder:
    """Build a source-uptick test configuration."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "base_url": "https://test-tenant.onuptick.com",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "username": "test-user",
            "password": "test-password",
        }

    def with_base_url(self, base_url: Any) -> "ConfigBuilder":
        self._config["base_url"] = base_url
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
