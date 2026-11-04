# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-mailersend test configurations."""

    def __init__(self) -> None:
        self._api_token = "test-api-token"
        self._domain_id = "example.com"
        self._start_date = 1788220800

    def with_api_token(self, api_token: str) -> "ConfigBuilder":
        self._api_token = api_token
        return self

    def with_domain_id(self, domain_id: str) -> "ConfigBuilder":
        self._domain_id = domain_id
        return self

    def with_start_date(self, start_date: int) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def build(self) -> Dict[str, Any]:
        return {"api_token": self._api_token, "domain_id": self._domain_id, "start_date": self._start_date}
