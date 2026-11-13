# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


ACCESS_TOKEN = "access-sandbox-token"
API_KEY = "test-secret"
CLIENT_ID = "test-client-id"
BASE_URL = "https://sandbox.plaid.com"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "access_token": ACCESS_TOKEN,
            "api_key": API_KEY,
            "client_id": CLIENT_ID,
            "plaid_env": "sandbox",
            "start_date": "2026-01-01",
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)


def credentials_body() -> Dict[str, Any]:
    return {"secret": API_KEY, "client_id": CLIENT_ID, "access_token": ACCESS_TOKEN}
