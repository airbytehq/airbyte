# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, MutableMapping


API_KEY = "test_api_key"
API_SECRET = "test_api_secret"
SHOP = "test-shop.example.com"
START_DATE = "2024-01-01"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "api_key": API_KEY,
            "api_secret": API_SECRET,
            "shop": SHOP,
            "start_date": START_DATE,
        }

    def with_api_key(self, api_key: str) -> ConfigBuilder:
        self._config["api_key"] = api_key
        return self

    def with_api_secret(self, api_secret: str) -> ConfigBuilder:
        self._config["api_secret"] = api_secret
        return self

    def with_shop(self, shop: str) -> ConfigBuilder:
        self._config["shop"] = shop
        return self

    def with_start_date(self, start_date: str) -> ConfigBuilder:
        self._config["start_date"] = start_date
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
