#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, List, MutableMapping, Optional


CLIENT_ID = "test_client_id"
CLIENT_SECRET = "test_client_secret"
REFRESH_TOKEN = "test_refresh_token"
ACCESS_TOKEN = "test_access_token"

ORGANIZATION_ID = "test_org_123"
AD_ACCOUNT_ID = "test_adaccount_456"
CAMPAIGN_ID = "test_campaign_789"
ADSQUAD_ID = "test_adsquad_012"
AD_ID = "test_ad_345"

START_DATE = "2024-01-01"
END_DATE = "2024-01-31"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "action_report_time": "conversion",
            "swipe_up_attribution_window": "28_DAY",
            "view_attribution_window": "1_DAY",
        }

    def with_client_id(self, client_id: str) -> "ConfigBuilder":
        self._config["client_id"] = client_id
        return self

    def with_client_secret(self, client_secret: str) -> "ConfigBuilder":
        self._config["client_secret"] = client_secret
        return self

    def with_refresh_token(self, refresh_token: str) -> "ConfigBuilder":
        self._config["refresh_token"] = refresh_token
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def with_end_date(self, end_date: str) -> "ConfigBuilder":
        self._config["end_date"] = end_date
        return self

    def with_organization_ids(self, organization_ids: List[str]) -> "ConfigBuilder":
        self._config["organization_ids"] = organization_ids
        return self

    def with_ad_account_ids(self, ad_account_ids: List[str]) -> "ConfigBuilder":
        self._config["ad_account_ids"] = ad_account_ids
        return self

    def with_action_report_time(self, action_report_time: str) -> "ConfigBuilder":
        self._config["action_report_time"] = action_report_time
        return self

    def with_swipe_up_attribution_window(self, window: str) -> "ConfigBuilder":
        self._config["swipe_up_attribution_window"] = window
        return self

    def with_view_attribution_window(self, window: str) -> "ConfigBuilder":
        self._config["view_attribution_window"] = window
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
