# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "account_token": "Fleetio Account Token",
            "api_key": "Fleetio API Token",
        }

    def with_account_token(self, account_token: str) -> "ConfigBuilder":
        self._config["account_token"] = account_token
        return self

    def with_api_key(self, api_key: str) -> "ConfigBuilder":
        self._config["api_key"] = api_key
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
