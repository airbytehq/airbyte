# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Mapping


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {
            "subdomain": "d3v-airbyte",
            "start_date": "2015-10-01T00:00:00Z",
            "credentials": {"credentials": "access_token", "access_token": "any_acces_token"},
        }

    def access_token(self, access_token: str) -> "ConfigBuilder":
        self._config["credentials"]["access_token"] = access_token
        return self

    def start_date(self, start_date: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def subdomain(self, subdomain: str) -> "ConfigBuilder":
        self._config["subdomain"] = subdomain
        return self

    def build(self) -> Mapping[str, Any]:
        return self._config
