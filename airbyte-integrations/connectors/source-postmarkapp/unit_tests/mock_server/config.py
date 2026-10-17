# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict


class ConfigBuilder:
    def __init__(self) -> None:
        self._server_token = "test-server-token"
        self._account_token = "test-account-token"
        self._start_date = None
        self._slice_window_minutes = None

    def with_start_date(self, start_date: str) -> "ConfigBuilder":
        self._start_date = start_date
        return self

    def with_slice_window_minutes(self, slice_window_minutes: int) -> "ConfigBuilder":
        self._slice_window_minutes = slice_window_minutes
        return self

    def build(self) -> Dict[str, Any]:
        config = {
            "X-Postmark-Server-Token": self._server_token,
            "X-Postmark-Account-Token": self._account_token,
        }
        if self._start_date is not None:
            config["start_date"] = self._start_date
        if self._slice_window_minutes is not None:
            config["slice_window_minutes"] = self._slice_window_minutes
        return config
