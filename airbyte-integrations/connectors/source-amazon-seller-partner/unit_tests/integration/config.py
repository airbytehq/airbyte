#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from datetime import datetime
from typing import Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, str] = {
            "refresh_token": "amazon_refresh_token",
            "lwa_app_id": "amazon_app_id",
            "lwa_client_secret": "amazon_client_secret",
            "replication_start_date": "2024-01-01T00:00:00Z",
            "aws_environment": "PRODUCTION",
            "region": "US",
            "account_type": "Seller",
        }

    def with_start_date(self, start_date: datetime) -> ConfigBuilder:
        self._config["replication_start_date"] = start_date.isoformat()[:-13] + "Z"
        return self

    def build(self) -> Dict[str, str]:
        return self._config
