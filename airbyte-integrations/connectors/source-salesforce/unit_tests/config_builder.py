# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Mapping


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "refresh_token": "fake_refresh_token",
            "auth_type": "refresh_token",
            "start_date": "2010-01-18T21:18:20Z",
            "is_sandbox": False,
            "wait_timeout": 15,
        }

    def start_date(self, start_date: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def stream_slice_step(self, stream_slice_step: str) -> "ConfigBuilder":
        self._config["stream_slice_step"] = stream_slice_step
        return self

    def client_id(self, client_id: str) -> "ConfigBuilder":
        self._config["client_id"] = client_id
        return self

    def client_secret(self, client_secret: str) -> "ConfigBuilder":
        self._config["client_secret"] = client_secret
        return self

    def refresh_token(self, refresh_token: str) -> "ConfigBuilder":
        self._config["refresh_token"] = refresh_token
        return self

    def auth_type(self, auth_type: str) -> "ConfigBuilder":
        self._config["auth_type"] = auth_type
        return self

    def domain_url(self, domain_url: str) -> "ConfigBuilder":
        self._config["domain_url"] = domain_url
        return self

    def with_client_credentials_auth(self, domain_url: str = "https://test-domain.my.salesforce.com") -> "ConfigBuilder":
        """Configure for client credentials authentication"""
        self._config["auth_type"] = "client_credentials"
        self._config["domain_url"] = domain_url
        # Remove refresh_token as it's not needed for client credentials
        self._config.pop("refresh_token", None)
        return self

    def build(self) -> Mapping[str, Any]:
        return self._config
