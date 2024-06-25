# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "auth_token": "test token",
            "organization": "test organization",
            "project": "test project",
            "hostname": "sentry.io"
        }

    def build(self) -> Dict[str, Any]:
        return self._config
