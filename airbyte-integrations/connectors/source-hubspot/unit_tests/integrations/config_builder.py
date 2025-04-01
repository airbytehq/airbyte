# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping


class ConfigBuilder:
    def __init__(self):
        self._config = {
            "enable_experimental_streams": True
        }

    def with_start_date(self, start_date: str):
        self._config["start_date"] = start_date
        return self

    def with_auth(self, credentials: Mapping[str, str]):
        self._config["credentials"] = credentials
        return self

    def build(self) -> Mapping[str, Any]:
        return self._config
