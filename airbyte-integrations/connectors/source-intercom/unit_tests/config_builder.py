# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Mapping


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {
            "access_token": "fake_access_token",
            "start_date": "2010-01-18T21:18:20Z",
        }

    def start_date(self, start_date: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def access_token(self, refresh_token: str) -> "ConfigBuilder":
        self._config["refresh_token"] = refresh_token
        return self

    def build(self) -> Mapping[str, Any]:
        return self._config
