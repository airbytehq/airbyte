#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

import datetime as dt
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
        self._config["start_date"] = dt.datetime.strptime(start_date, DATE_TIME_FORMAT).strftime(DATE_TIME_FORMAT)
        return self

    def with_access_token(self, access_token: str) -> ConfigBuilder:
        self._config["access_token"] = access_token
        return self

    def build(self) -> MutableMapping[str, Any]:
        return self._config
