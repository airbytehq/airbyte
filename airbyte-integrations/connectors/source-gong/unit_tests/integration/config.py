#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, MutableMapping


ACCESS_KEY = "test_access_key"
ACCESS_KEY_SECRET = "test_access_key_secret"

WORKSPACE_ID = "test_workspace_123"
FOLDER_ID = "test_folder_456"
CALL_ID = "test_call_789"
TRACKER_ID = "test_tracker_012"
USER_ID = "test_user_345"
SCORECARD_ID = "test_scorecard_678"
ANSWERED_SCORECARD_ID = "test_answered_scorecard_901"

START_DATE = "2024-01-01T00:00:00Z"


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "access_key": ACCESS_KEY,
            "access_key_secret": ACCESS_KEY_SECRET,
            "start_date": START_DATE,
        }

    def with_access_key(self, access_key: str) -> "ConfigBuilder":
        self._config["access_key"] = access_key
        return self

    def with_access_key_secret(self, access_key_secret: str) -> "ConfigBuilder":
        self._config["access_key_secret"] = access_key_secret
        return self

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._config["start_date"] = start_date
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
