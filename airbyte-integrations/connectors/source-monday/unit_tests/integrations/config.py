# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._credentials: Dict[str, str] = {}

    def with_oauth_credentials(self, client_id: str, client_secret: str, access_token: str, subdomain: str) -> "ConfigBuilder":
        self._credentials["auth_type"] = "oauth2.0"
        self._credentials["client_id"] = client_id
        self._credentials["client_secret"] = client_secret
        self._credentials["access_token"] = access_token
        self._credentials["subdomain"] = subdomain
        return self

    def with_api_token_credentials(self, api_token: str) -> "ConfigBuilder":
        self._credentials["api_token"] = api_token
        self._credentials["auth_type"] = "api_token"
        return self

    def build(self) -> Dict[str, Any]:
        config = {}
        if self._credentials:
            config["credentials"] = self._credentials
        return config
