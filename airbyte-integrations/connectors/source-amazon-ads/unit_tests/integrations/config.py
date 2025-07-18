# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import datetime
from typing import Any, Dict, List

from airbyte_cdk.test.mock_http.response_builder import find_template


CLIENT_ID = "amzn.app-oa2-client.test"
CLIENT_SECRET = "test-secret"
REGION = "NA"
REPORT_WAIT_TIMEOUT = 120
PROFILES = [1]


class ConfigBuilder:
    def __init__(self) -> None:
        oauth_fixture: Dict[str, Any] = find_template("oauth", __file__)
        self._access_token: str = oauth_fixture["access_token"]
        self._refresh_token: str = oauth_fixture["refresh_token"]
        self._client_id: str = CLIENT_ID
        self._client_secret: str = CLIENT_SECRET
        self._region: str = REGION
        self._report_wait_timeout: str = REPORT_WAIT_TIMEOUT
        self._profiles: str = PROFILES
        self._start_date: str = None

    def with_client_id(self, client_id: str) -> "ConfigBuilder":
        self._client_id = client_id
        return self

    def with_client_secret(self, client_secret: str) -> "ConfigBuilder":
        self._client_secret = client_secret
        return self

    def with_access_token(self, access_token: str) -> "ConfigBuilder":
        self._access_token = access_token
        return self

    def with_refresh_token(self, refresh_token: str) -> "ConfigBuilder":
        self._refresh_token = refresh_token
        return self

    def with_region(self, region: str) -> "ConfigBuilder":
        self._region = region
        return self

    def with_report_wait_timeout(self, report_wait_timeout: int) -> "ConfigBuilder":
        self._report_wait_timeout = report_wait_timeout
        return self

    def with_profiles(self, profiles: List[int]) -> "ConfigBuilder":
        self._profiles = profiles
        return self

    def with_start_date(self, start_date: datetime.date) -> "ConfigBuilder":
        self._start_date = start_date.isoformat()
        return self

    def build(self) -> Dict[str, Any]:
        config = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "region": self._region,
            "report_wait_timeout": self._report_wait_timeout,
            "profiles": self._profiles,
        }
        if self._start_date:
            config["start_date"] = self._start_date
        return config
