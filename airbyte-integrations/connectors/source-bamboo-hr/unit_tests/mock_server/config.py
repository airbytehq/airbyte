# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


class ConfigBuilder:
    def __init__(self) -> None:
        self._config = {
            "api_key": "test-key",
            "subdomain": "test-company",
            "start_date": "2026-11-01T00:00:00Z",
            "employee_fields": "workEmail,terminationDate,lastName",
            "custom_reports_fields": "lastName",
            "custom_reports_include_default_fields": True,
        }

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
