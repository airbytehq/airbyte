# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._report_ids = []
        self._access_token = None

    def with_access_token(self, access_token: str) -> "ConfigBuilder":
        self._access_token = access_token
        return self

    def rest_build(self) -> Dict[str, Any]:
        self._config: Dict[str, Any] = {
            "tenant_id": "test_tenant",
            "host": "test_host",
            "start_date": "2024-05-01T00:00:00.000Z",
            "credentials": {
                "access_token": self._access_token,
            },
        }

        return self._config
