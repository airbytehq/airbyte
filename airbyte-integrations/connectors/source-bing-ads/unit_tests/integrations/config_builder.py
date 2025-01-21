# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import find_template


TENNANT_ID = "common"
DEVELOPER_TOKEN = "test-token"
REFRESH_TOKEN = "test-refresh-token"
CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"
LOOKBACK_WINDOW = 0


class ConfigBuilder:
    def __init__(self) -> None:
        oauth_fixture: Dict[str, Any] = find_template("oauth", __file__)
        self._access_token: str = oauth_fixture["access_token"]
        self._refresh_token: str = oauth_fixture["refresh_token"]
        self._client_id: str = CLIENT_ID
        self._client_secret: str = CLIENT_SECRET
        self._refresh_token: str = REFRESH_TOKEN
        self._developer_token: str = DEVELOPER_TOKEN
        self._tenant_id: str = TENNANT_ID
        self._report_start_date: str = None
        self._lookback_window: int = LOOKBACK_WINDOW

    def with_reports_start_date(self, start_date: str) -> "ConfigBuilder":
        self._report_start_date = start_date
        return self

    def build(self) -> Dict[str, Any]:
        config = {
            "tenant_id": self._tenant_id,
            "developer_token": self._developer_token,
            "refresh_token": self._refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "lookback_window": self._lookback_window,
        }
        if self._report_start_date:
            config["reports_start_date"] = self._report_start_date
        return config
