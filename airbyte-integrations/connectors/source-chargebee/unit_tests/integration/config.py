# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {
            "site": "ConfigBuilder default site",
            "site_api_key": "ConfigBuilder default site api key",
            "start_date": "2023-01-01T06:57:44Z",
            "product_catalog": "2.0",
        }

    def with_site(self, site: str) -> "ConfigBuilder":
        self._config["site"] = site
        return self

    def with_site_api_key(self, site_api_key: str) -> "ConfigBuilder":
        self._config["site_api_key"] = site_api_key
        return self

    def with_start_date(self, start_datetime: datetime) -> "ConfigBuilder":
        self._config["start_date"] = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self

    def with_product_catalog(self, product_catalog: str) -> "ConfigBuilder":
        self._config["product_catalog"] = product_catalog or "2.0"
        return self

    def build(self) -> Dict[str, Any]:
        return self._config
