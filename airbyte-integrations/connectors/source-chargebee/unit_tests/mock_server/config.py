# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, MutableMapping


# Constants for test data - match connector's spec
SITE_API_KEY = "test_api_key_12345"
SITE = "test-site"
START_DATE = "2024-01-01T00:00:00Z"
PRODUCT_CATALOG = "2.0"


class ConfigBuilder:
    """Builder for creating test configurations matching connector spec."""

    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "site_api_key": SITE_API_KEY,
            "site": SITE,
            "start_date": START_DATE,
            "product_catalog": PRODUCT_CATALOG,
        }

    def with_site_api_key(self, site_api_key: str) -> "ConfigBuilder":
        self._config["site_api_key"] = site_api_key
        return self

    def with_site(self, site: str) -> "ConfigBuilder":
        self._config["site"] = site
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_product_catalog(self, product_catalog: str) -> "ConfigBuilder":
        self._config["product_catalog"] = product_catalog
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
