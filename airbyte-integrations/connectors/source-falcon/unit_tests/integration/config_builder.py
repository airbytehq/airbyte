# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._report_ids = []

    def with_report_id(self, report_id: str) -> "ConfigBuilder":
        self._report_ids = [report_id]
        return self

    def build(self) -> Dict[str, Any]:
        self._config: Dict[str, Any] = {
            "username": "test_user",
            "password": "test_password",
            "tenant_id": "test_tenant",
            "report_ids": self._report_ids,
            "host": "test_host"
        }
        return self._config
