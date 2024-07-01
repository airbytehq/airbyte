# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "credentials": {
                "auth_type": "oauth2.0",
                "access_token": "access token",
                "app_id": "11111111111111111111",
                "secret": "secret"
            },
            "start_date": "2024-01-01",
            "include_deleted": False
        }

    def with_include_deleted(self) -> "ConfigBuilder":
        self._config["include_deleted"] = True
        return self

    def with_end_date(self, date: str) -> "ConfigBuilder":
        self._config["end_date"] = date
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
