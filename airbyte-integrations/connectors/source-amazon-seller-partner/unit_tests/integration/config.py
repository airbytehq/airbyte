#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from datetime import datetime
from typing import Dict

import pendulum


ACCESS_TOKEN = "test_access_token"
LWA_APP_ID = "amazon_app_id"
LWA_CLIENT_SECRET = "amazon_client_secret"
MARKETPLACE_ID = "ATVPDKIKX0DER"
REFRESH_TOKEN = "amazon_refresh_token"

CONFIG_START_DATE = "2023-01-01T00:00:00Z"
CONFIG_END_DATE = "2023-01-30T00:00:00Z"
VENDOR_TRAFFIC_REPORT_CONFIG_END_DATE = "2023-01-01T23:59:59Z"
NOW = pendulum.now(tz="utc")
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: Dict[str, str] = {
            "refresh_token": REFRESH_TOKEN,
            "lwa_app_id": LWA_APP_ID,
            "lwa_client_secret": LWA_CLIENT_SECRET,
            "replication_start_date": CONFIG_START_DATE,
            "replication_end_date": CONFIG_END_DATE,
            "aws_environment": "PRODUCTION",
            "region": "US",
            "account_type": "Seller",
        }

    def with_start_date(self, start_date: datetime) -> ConfigBuilder:
        self._config["replication_start_date"] = start_date.strftime(TIME_FORMAT)
        return self

    def with_end_date(self, end_date: datetime) -> ConfigBuilder:
        self._config["replication_end_date"] = end_date.strftime(TIME_FORMAT)
        return self

    def build(self) -> Dict[str, str]:
        return self._config
