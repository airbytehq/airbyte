#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, List, MutableMapping

from airbyte_cdk.utils.datetime_helpers import ab_datetime_now


ACCESS_TOKEN = "test_access_token"
ACCOUNT_ID = "111111111111111"
CLIENT_ID = "test_client_id"
CLIENT_SECRET = "test_client_secret"
DATE_FORMAT = "%Y-%m-%d"
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
NOW = ab_datetime_now()
_start_dt = (NOW - timedelta(days=365)).replace(hour=0, minute=0, second=0, microsecond=0)
START_DATE = _start_dt.strftime(DATE_TIME_FORMAT)
END_DATE = _start_dt.replace(hour=23, minute=59, second=59).strftime(DATE_TIME_FORMAT)
START_DATE_EPOCH = int(_start_dt.timestamp())


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "account_ids": [ACCOUNT_ID],
            "access_token": ACCESS_TOKEN,
            "credentials": {
                "auth_type": "Service",
                "access_token": ACCESS_TOKEN,
            },
            "start_date": START_DATE,
            "end_date": END_DATE,
            "include_deleted": True,
            "fetch_thumbnail_images": True,
            "custom_insights": [],
            "page_size": 100,
            "insights_lookback_window": 28,
            "insights_job_timeout": 60,
            "action_breakdowns_allow_empty": True,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

    def with_account_ids(self, account_ids: List[str]) -> ConfigBuilder:
        self._config["account_ids"] = account_ids
        return self

    def with_start_date(self, start_date: datetime) -> ConfigBuilder:
        self._config["start_date"] = start_date.strftime(DATE_TIME_FORMAT)
        return self

    def with_end_date(self, end_date: datetime) -> ConfigBuilder:
        self._config["end_date"] = end_date.strftime(DATE_TIME_FORMAT)
        return self

    def with_ad_statuses(self, statuses: List[str]) -> ConfigBuilder:
        self._config["ad_statuses"] = statuses
        return self

    def with_campaign_statuses(self, statuses: List[str]) -> ConfigBuilder:
        self._config["campaign_statuses"] = statuses
        return self

    def with_ad_set_statuses(self, statuses: List[str]) -> ConfigBuilder:
        self._config["adset_statuses"] = statuses
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
