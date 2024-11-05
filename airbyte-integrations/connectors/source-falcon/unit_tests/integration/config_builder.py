# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._report_ids = []
        self._access_token = None

    def with_report_id(self, report_id: str) -> "ConfigBuilder":
        self._report_ids = [report_id]
        return self

    def with_access_token(self, access_token: str) -> "ConfigBuilder":
        self._access_token = access_token
        return self

    def raas_build(self) -> Dict[str, Any]:
        self._config: Dict[str, Any] = {
            "tenant_id": "test_tenant",
            "host": "test_host",
            "credentials": {
                "username": "test_user",
                "password": "test_password",
                "report_ids": self._report_ids,
                "auth_type": "RAAS"
            }
        }

        return self._config

    def rest_build(self) -> Dict[str, Any]:
        self._config: Dict[str, Any] = {
            "tenant_id": "test_tenant",
            "host": "test_host",
            "credentials": {
                "access_token": self._access_token,
                "start_date": "2024-05-01T00:00:00.000Z",
                "auth_type": "REST"
            }
        }

        return self._config
