# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


BUSINESS_UNIT_ID = "0Uv000000000001AAA"
START_DATE = "2024-01-01T00:00:00Z"
# The start date as the version 5 streams send and save it: their cursor format ends in a literal "-12:00".
START_CURSOR = "2024-01-01T00:00:00-12:00"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "pardot_business_unit_id": BUSINESS_UNIT_ID,
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
            "start_date": START_DATE,
            "is_sandbox": False,
        }

    def with_is_sandbox(self, is_sandbox: bool) -> "ConfigBuilder":
        self._config["is_sandbox"] = is_sandbox
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._config)
