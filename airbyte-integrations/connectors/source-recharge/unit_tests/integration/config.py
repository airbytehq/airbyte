#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import Any, MutableMapping

import pendulum


START_DATE = "2023-01-01T00:00:00Z"
ACCESS_TOKEN = "test_access_token"
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
NOW = pendulum.now(tz="utc")


class ConfigBuilder:
    def __init__(self) -> None:
        self._config: MutableMapping[str, Any] = {
            "access_token": ACCESS_TOKEN,
            "start_date": START_DATE,
        }

    def with_start_date(self, start_date: str) -> ConfigBuilder:
        # Stored verbatim, not reformatted through DATE_TIME_FORMAT (%z): the
        # connector's spec requires start_date as literal ...Z (see spec.json's
        # pattern and START_DATE above), not a %z offset like +0000. Every
        # stream's start_datetime.datetime_format expects that same ...Z shape.
        self._config["start_date"] = start_date
        return self

    def with_access_token(self, access_token: str) -> ConfigBuilder:
        self._config["access_token"] = access_token
        return self

    def with_lookback_window_days(self, lookback_window_days: int) -> ConfigBuilder:
        self._config["lookback_window_days"] = lookback_window_days
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
