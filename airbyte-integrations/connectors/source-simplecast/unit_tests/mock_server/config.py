# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    """Builder for source-simplecast test configurations."""

    def __init__(self) -> None:
        self._api_token: str = "test-api-token"

    def with_api_token(self, api_token: str) -> "ConfigBuilder":
        self._api_token = api_token
        return self

    def build(self) -> Dict[str, Any]:
        return {"api_token": self._api_token}
