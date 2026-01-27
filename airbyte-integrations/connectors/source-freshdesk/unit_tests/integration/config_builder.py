# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Mapping


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {
            "api_key": "fake_api_key",
            "domain": "any-domain.freshdesk.com",
            "start_date": "2010-01-18T21:18:20Z",
        }

    def start_date(self, start_date: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def api_key(self, api_key: str) -> "ConfigBuilder":
        self._config["api_key"] = api_key
        return self

    def domain(self, domain: str) -> "ConfigBuilder":
        self._config["domain"] = domain
        return self

    def build(self) -> Mapping[str, Any]:
        return self._config
