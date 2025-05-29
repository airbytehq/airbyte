# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "account_id": "an account id",
            "replication_start_date": "2021-01-01T00:00:00Z",
            "credentials": {
                "api_token": "an api key",
                "auth_type": "Token"
            }
        }

    def with_account_id(self, account_id: str) -> "ConfigBuilder":
        self._config["account_id"] = account_id
        return self

    def with_replication_start_date(self, replication_start_date: datetime) -> "ConfigBuilder":
        self._config["replication_start_date"] = replication_start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return self

    def with_api_token(self, api_token: str) -> "ConfigBuilder":
        self._config["credentials"]["api_token"] = api_token
        return self

    def with_client_id(self, client_id: str) -> "ConfigBuilder":
        self._config["credentials"]["client_id"] = client_id
        return self

    def with_auth_type(self, auth_type: str) -> "ConfigBuilder":
        self._config["credentials"]["auth_type"] = auth_type
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
