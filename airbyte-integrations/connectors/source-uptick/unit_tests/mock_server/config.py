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

    def with_password_credentials(self) -> "ConfigBuilder":
        """Move the credential fields under `credentials` with auth_type password."""
        credentials = {field: self._config.pop(field) for field in ("client_id", "client_secret", "username", "password")}
        credentials["auth_type"] = "password"
        self._config["credentials"] = credentials
        return self

    def with_oauth_credentials(
        self,
        refresh_token: str = "test-refresh-token",
        access_token: str | None = None,
        token_expiry_date: str | None = None,
    ) -> "ConfigBuilder":
        """Replace the credential fields with an OAuth 2.0 `credentials` block.

        Pass `access_token` and `token_expiry_date` to get the shape the platform persists after
        consent or a refresh CONTROL; without them every run starts with a cold refresh.
        """
        for field in ("client_id", "client_secret", "username", "password"):
            self._config.pop(field, None)
        self._config["credentials"] = {
            "auth_type": "oauth2.0",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": refresh_token,
        }
        if access_token is not None:
            self._config["credentials"]["access_token"] = access_token
        if token_expiry_date is not None:
            self._config["credentials"]["token_expiry_date"] = token_expiry_date
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
