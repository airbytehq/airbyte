# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


TOKEN_URL = "https://zoom.us/oauth/token"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "account_id": "test_account_id",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "authorization_endpoint": TOKEN_URL,
        }

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
