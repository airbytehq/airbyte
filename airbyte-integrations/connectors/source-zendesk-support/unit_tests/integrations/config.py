# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import base64
from typing import Any, Dict

from pendulum.datetime import DateTime


class ConfigBuilder:
    def __init__(self) -> None:
        self._subdomain: str = None
        self._start_date: str = None
        self._credentials: Dict[str, str] = {}

    def with_subdomain(self, subdomain: str) -> "ConfigBuilder":
        self._subdomain = subdomain
        return self

    def with_oauth_credentials(self, access_token: str) -> "ConfigBuilder":
        self._credentials["access_token"] = access_token
        self._credentials["credentials"] = "oauth2.0"
        return self

    def with_basic_auth_credentials(self, email: str, password: str) -> "ConfigBuilder":
        self._credentials["api_token"] = password
        self._credentials["credentials"] = "api_token"
        self._credentials["email"] = email
        return self

    def with_start_date(self, start_date: DateTime) -> "ConfigBuilder":
        self._start_date = start_date.format("YYYY-MM-DDTHH:mm:ss[Z]")
        return self

    def build(self) -> Dict[str, Any]:
        config = {}
        if self._subdomain:
            config["subdomain"] = self._subdomain
        if self._start_date:
            config["start_date"] = self._start_date
        if self._credentials:
            config["credentials"] = self._credentials
        return config
