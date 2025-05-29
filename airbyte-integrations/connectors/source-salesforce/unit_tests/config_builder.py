# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Mapping


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "refresh_token": "fake_refresh_token",
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

    def build(self) -> Mapping[str, Any]:
        return self._config
